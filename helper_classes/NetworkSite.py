#!/usr/bin/env python2.7

from RouterConnection import RouterConnection
from NetworkHelpers import get_hostname_from_ip, get_ip
from ParseHelpers import parse_info
import pyodbc
import datetime
import statistics
import re
import threading
import logging
import ipaddress
import paramiko
import traceback
import certifi
from elasticsearch import Elasticsearch


class NetworkSite:
    """
    This class provides an easy way to connect to the mpls router, vpn router,
    and core switch at a given site and perform a series of checks on them.
    """

    # global instance of elasticsearch client, static class variable
    es = Elasticsearch(
        ['snpstemp054'],
        http_auth=('andrew', 'km+/;"#MU9"bhxySGH6y'),
        port=9200,
    )

    # constants
    # maximum utilization
    __UTILIZATION_THRESHOLD = 80

    # multiplication factor for MPLS utilization
    __MPLS_UTILIZATION_CORRECTION = 0.85

    # bit conversion from kilobits
    __BIT_CONVERSION = 1000

    # conversion from decimal to percent
    __PERCENTAGE_CONVERSION = 100

    # number of pings
    __PING_AMOUNT = 30

    # number of extra connections used for multithreading
    __MAX_EXTRA_CONNECTIONS = 3

    # minimum pfx_rcd for BGP status checks
    __BGP_THRESHOLD = 460

    # days of Solarwind data used to calculate historical latency
    __NUM_HIST_DAYS = 2

    # minimum ping percentage
    __PING_THRESHOLD = 100

    # maximum time to live
    __MAX_HOPS = 30

    # used for log in to server
    __USERNAME = 'andchan'
    __PASSWORD = 'Taser!123123'

    # status
    __PASS = 0
    __INCOMPLETE = 1
    __FAIL = 2
    __NOT_RUN = 3


    # CONSTRUCTOR
    def __init__(self, site):
        """
        :type site: string
        :rtype: void

        CONSTRUCTOR:
        Creates an instance of the NetworkSite class. Attempts to connect to the core switch,
        mpls router, and vpn router at the site. Also fetches the historical latency information
        for the given site from the Solarwinds SQL database.

        EXAMPLE USAGE:
        site_connect = NetworkSite('us11')
        """
        self.__site = site.lower()
        self.__initialize_latency_table()

        self.__set_mpls_router()
        self.__set_vpn_router()
        self.__set_core_switch()

        self.__set_logger()



    # PUBLIC METHODS
    def check_bgp_status(self):
        """
        :rtype: Dict

        PUBLIC METHOD:
        Used to get the BGP status for a site. Checks both VPN and MPLS routers to see whether interfaces are up and have sufficient state.

        EXAMPLE USAGE:
        bgp_json = site_connection.check_BGP_status()
        """
        if not self.__mpls_router.is_connected() and not self.__vpn_router.is_connected():
            return {'status': self.__NOT_RUN, 'message': 'No existing MPLS router or failed connection. No existing VPN router or failed connection.'}

        all_info = {'status': self.__PASS, 'routers': []}

        # used to generate message
        fail = []
        incomplete = []

        if self.__mpls_router.is_connected():
            mpls_info = self.__test_MPLS_BGP()
            all_info['routers'].append(mpls_info)

        if self.__vpn_router.is_connected():
            vpn_info = self.__test_VPN_BGP()
            all_info['routers'].append(vpn_info)

        # loop through routers and set appropriate status
        for info in all_info['routers']:
            if info['status'] == self.__FAIL:
                # set status to FAIL regardless of past status
                all_info['status'] = self.__FAIL
                fail.append(info['router'])

            elif info['status'] == self.__INCOMPLETE:
                incomplete.append(info['router'])
                if all_info['status'] == self.__PASS:
                    # set incomplete ONLY if past status was passing
                    all_info['status'] = self.__INCOMPLETE

        # set message
        if all_info['status'] == self.__PASS:
            all_info['message'] = 'Interfaces for all device(s) are up and have sufficient state.'
        elif all_info['status'] == self.__FAIL:
            all_info['message'] = 'Interfaces for {0} are down or have insufficient state.'.format(' and '.join(fail))
        else:
            all_info['message'] = 'Tests for {0} failed to complete. See results for more details.'.format(' and '.join(incomplete))

        self.__logging_wrapper('BGP-STATUS', all_info['status'], all_info['message'])

        return all_info


    def check_interface_errors(self):
        """
        :rtype: Dict

        PUBLIC METHOD:
        Checks for interface errors. Tests out the MPLS / VPN routers and core switch for a given site and then checks the interfaces  that have 'up' status in the Status and Protocol
        columns. Checks to see that these interfaces have 0 input errors, 0 CRC, 0 output errors, 0 collisions, 0 resets, and 0 total drops. Currently does not 
        clear the counters for the interface, but that line can be commented back in the __get_error_counts function. Returns information as a JSON object.
        
        Example Usage:
        info = site_connection.check_interface_errors()
        """
        if not self.__mpls_router.is_connected() and not self.__vpn_router.is_connected() and not self.__core_switch.is_connected():
            return {'status': self.__NOT_RUN, 'message': 'No existing MPLS router or failed connection. No existing VPN router or failed connection. Failed connection to core switch.'}

        # boolean that stores whether any interface has errors
        all_errors = {'status': self.__PASS, 'interfaces': []}

        # used to set message, using set to prevent repeats
        fail = set()
        incomplete = set()

        for router_connect in [self.__mpls_router, self.__vpn_router, self.__core_switch]:
            if not router_connect.is_connected():
                continue

            output = router_connect.execute_short('sh ip int brief | i up.+up')
            if output == None:
                # command failed
                all_errors['interfaces'].insert(0, {'router': router_connect.get_name(), 'status': self.__INCOMPLETE, 'message': 'Command \'sh ip int brief | i up.+up\' failed for {0}.'.format(router_connect.get_name())})
                
                incomplete.add(router_connect.get_name())
                # if currently passing, set to incomplete
                if all_errors['status'] == self.__PASS:
                    all_errors['status'] = self.__INCOMPLETE

                continue

            all_interfaces = re.findall(r'(\S+)\s+\d+[.]\d+[.]\d+[.]\d+.+up\s+up', output)
            for interface in all_interfaces:
                # not real interface
                if interface == 'NVI0':
                    continue

                errors = self.__get_error_counts(interface, router_connect)
                all_errors['interfaces'].append(errors)

                if errors['status'] == self.__FAIL:
                    all_errors['status'] = self.__FAIL
                    fail.add(router_connect.get_name())

                elif errors['status'] == self.__INCOMPLETE:
                    incomplete.add(router_connect.get_name())
                    if all_errors['status'] == self.__PASS:
                        all_errors['status'] = self.__INCOMPLETE


        if all_errors['status'] == self.__PASS:
            all_errors['message'] = 'No interfaces had any errors.'
        elif all_errors['status'] == self.__FAIL:
            all_errors['message'] = 'At least one interface on device(s) {0} had errors.'.format(', '.join(fail))
        else:
            all_errors['message'] = 'At least one test on device(s) {0} failed to complete. See results for more details.'.format(', '.join(incomplete))

        self.__logging_wrapper('INTERFACE-ERROR', all_errors['status'], all_errors['message'])

        return all_errors


    def check_mpls_wan_utilization(self):
        """
        rtype: Dict

        PUBLIC METHOD:
        Checks whether the utilization of the mpls router is sufficient (above the specified
        UTILIZATION_THRESHOLD). Returns a dictionary.

        Example Usage:
        mpls_wan_utilization_info = site_connection.check_mpls_wan_utilization()
        """
        if not self.__mpls_router.is_connected():
            return {'status': self.__NOT_RUN, 'message': 'No existing MPLS router or failed connection.'}

        return self.__has_acceptable_utilization(self.__mpls_router, True, 'MPLS-WAN-UTILIZATION')


    def check_vpn_internet_utilization(self):
        """
        rtype: Dict

        PUBLIC METHOD:
        Checks whether the utilization of the vpn router is sufficient (above the specified
        UTILIZATION_THRESHOLD). Returns a dictionary.

        Example Usage:
        vpn_internet_utilization_info = site_connection.check_vpn_internet_utilization()
        """
        if not self.__vpn_router.is_connected():
            return {'status': self.__NOT_RUN, 'message': 'No existing VPN router or failed connection.'}

        return self.__has_acceptable_utilization(self.__vpn_router, False, 'VPN-INTERNET-UTILIZATION')


    def check_core_switch_ping(self):
        """
        :rtype: Dict

        PUBLIC METHOD:
        Checks the packet loss and latency, returned by pinging 7 sites from a given core switch. Returns an error if the percentage of success for the ping is not 100,
        and compares the numbers for the avg round-trip time to the latency figures stored in Solarwinds.

        Example Usage:
        site_connection.check_core_switch_ping()
        """
        # use core switch
        if not self.__core_switch.is_connected():
            return {'status': self.__NOT_RUN, 'message': 'Failed connection to core switch.'}

        # gets maximum number of available connections to cswitch
        all_switch_connects = self.__get_multiple_connections(self.__core_switch.get_name(), 'cisco_xe')
        all_switch_connects.append(self.__core_switch)

        # runs the pings
        all_ip_info = [
            {'ip': '10.12.136.29', 'name': 'us02-ipsla-router'},
            {'ip': '10.44.33.250', 'name': 'ca06-vpn-router'},
            {'ip': '10.130.32.250', 'name': 'cn42-vpn-router'},
            {'ip': '10.225.0.249', 'name': 'mdc-vpn-router'},
            {'ip': '10.144.193.104', 'name': 'indc-vpn-router'},
            {'ip': '10.116.65.240', 'name': 'am04-vpn-router-1'},
            {'ip': '10.128.32.19', 'name': 'jp01-vpn-router'},
        ]

        output_info = self.__run_parallel_pings(all_switch_connects, all_ip_info, self.__ping_helper_WAN, 'CORE-SWITCH-PING')
        return output_info


    def check_mpls_path(self):
        """
        :rtype: Dict

        PUBLIC METHOD:
        Checks to see that both the paths going in and out of the given core switch are taking MPLS paths.

        Example Usage:
        info = site_connection.check_mpls_path()
        """
        if not self.__core_switch.is_connected():
            return {'status': self.__NOT_RUN, 'message': 'Failed connection to core switch.'}
        elif not self.__mpls_router.is_connected():
            return {'status': self.__NOT_RUN, 'message': 'No existing MLPS router or failed connection.'}
        elif (self.__site in ['us02', 'de02', 'us6a', 'us03', 'jp01']):
            return {'status': self.__NOT_RUN, 'message': 'MPLS path is configured differently on this site (point to point, hub, etc.).'}

        # gets the proper trace address depending on whether or not given core switch is found in HQ
        cswitch_ip = get_ip(self.__core_switch)
        if cswitch_ip == None:
            self.__logging_wrapper('MPLS-PATH', self.__INCOMPLETE, 'Failed to resolve {0} to IP.'.format(self.__core_switch.get_name()))
            return {'status': self.__INCOMPLETE, 'message': 'Failed to resolve {0} to IP.'.format(self.__core_switch.get_name())}

        # convert to unicode
        cswitch_ip = unicode(cswitch_ip, 'utf-8')

        trace_address = '10.4.127.242' if (ipaddress.ip_address(cswitch_ip) in ipaddress.ip_network(u'10.8.0.0/13')) else '10.12.238.156'

        all_info = {'directions': [], 'status': self.__PASS}

        out_info = self.__check_out_path(trace_address)
        in_info = self.__check_in_path(cswitch_ip)

        all_info['directions'].append(out_info)
        all_info['directions'].append(in_info)

        # used to set message
        fail = []
        incomplete = []

        # set the status
        for info in all_info['directions']:
            if info['status'] == self.__FAIL:
                all_info['status'] = self.__FAIL
                fail.append(info['direction'])

            elif info['status'] == self.__INCOMPLETE:
                incomplete.append(info['direction'])
                if all_info['status'] == self.__PASS:
                    all_info['status'] = self.__INCOMPLETE

        if all_info['status'] == self.__PASS:
            all_info['message'] = 'Both inbound and outbound traffic take MPLS path.'
        elif all_info['status'] == self.__FAIL:
            all_info['message'] = 'Traffic for {0} direction(s) takes VPN path.'.format(' and '.join(fail))
        else:
            all_info['message'] = 'Tests for {0} direction(s) failed to complete. See results for more details.'.format(' and '.join(incomplete))

        self.__logging_wrapper('MPLS-PATH', all_info['status'], all_info['message'])

        return all_info


    def check_vpn_ping_pe_ip(self):
        """
        Checks packet loss to PE IP. Determines whether the vpn router is VRF or non-VRF and finds the corresponding PE IP. Pings the PE IP
        from the VPN router. If there is any packet loss, the function returns false.
        """
        if not self.__vpn_router.is_connected():
            return {'status': self.__NOT_RUN, 'message': 'No existing VPN router or failed connection.'}

        PE_address, PE_address_found = self.__get_PE_IP(self.__vpn_router)
        if not PE_address_found:
            # PE_address is the error message
            self.__logging_wrapper('VPN-PING-PE-IP', self.__INCOMPLETE, PE_address)
            return {'status': self.__INCOMPLETE, 'source': self.__vpn_router.get_name(), 'message': PE_address}

        info = self.__ping_test(self.__vpn_router, PE_address)
        if type(info) == str:
            self.__logging_wrapper('VPN-PING-PE-IP', self.__INCOMPLETE, info)
            return {'status': self.__INCOMPLETE, 'source': self.__vpn_router.get_name(), 'dest': PE_address, 'message': info}
        else:
            output_info = self.__create_message_object(self.__vpn_router, PE_address, info)
            self.__logging_wrapper('VPN-PING-PE-IP', output_info['status'], output_info['message'])
            return output_info


    def check_vpn_ping_hq(self):
        """
        :rtype: Dict

        PUBLIC METHOD:
        Checks packet loss when pinging from a certain site to HQ. If there is any packet loss or if the latency exceeds the historical latency
        by too large of an amount, the function will report an error. This function currently overlaps with check_vpn_ping_trace, and if no longer needed
        can be deleted.
        """
        if not self.__vpn_router.is_connected():
            return {'status': self.__NOT_RUN, 'message': 'No existing VPN router or failed connection.'}

        info = self.__ping_test(self.__vpn_router, '198.182.41.251')
        if type(info) == str:
            self.__logging_wrapper('VPN-PING-HQ', self.__INCOMPLETE, info)
            return {'status': self.__INCOMPLETE, 'source': self.__vpn_router.get_name(), 'dest': '198.182.41.251', 'message': info}
        else:
            output_info = self.__create_message_object(self.__vpn_router, '198.182.41.251', info)
            self.__logging_wrapper('VPN-PING-HQ', output_info['status'], output_info['message'])
            return output_info


    def check_vpn_ping_trace(self):
        """
        :rtype: Dict

        PUBLIC METHOD:
        Pings and traces the list of all_ips, which correspond to major hubs worldwide. Basically does the same thing as check_packet_loss_HQ(), 
        for all of the sites in the list.

        Example Usage:
        info = site_connection.check_vpn_ping_trace()
        """
        # use core switch
        if not self.__vpn_router.is_connected():
            return {'status': self.__NOT_RUN, 'message': 'No existing VPN router or failed connection.'}

        # gets maximum number of available connections to cswitch
        all_switch_connects = self.__get_multiple_connections(self.__vpn_router.get_name(), 'cisco_ios')
        all_switch_connects.append(self.__vpn_router)

        # HQ, MDC, INDC, JP01, CN42, CA06
        all_ip_info = [
            {'ip': '198.182.41.251', 'name': 'us02'},
            {'ip': '198.182.39.5', 'name': 'mdc'},
            {'ip': '198.182.52.30', 'name': 'indc'},
            {'ip': '198.182.50.1', 'name': 'jp01'},
            {'ip': '211.148.29.225', 'name': 'cn42'},
            {'ip': '69.90.0.217', 'name': 'ca06'}
        ]

        # runs the pings
        output_info = self.__run_parallel_pings(all_switch_connects, all_ip_info, self.__ping_helper_VPN, 'VPN-PING-TRACE')
        return output_info


    def finish(self):
        """
        :rtype: void

        PUBLIC METHOD:
        Used to disconnect properly from all the devices. Called when tests are finished.

        EXAMPLE USAGE:
        site_connection.finish()
        """
        if self.__vpn_router.is_connected():
            self.__vpn_router.disconnect()
        if self.__mpls_router.is_connected():
            self.__mpls_router.disconnect()
        if self.__core_switch.is_connected():
            self.__core_switch.disconnect()



    # PRIVATE METHODS
    def __logging_wrapper(self, test_name, status, message):
        """
        :type test_name: string
        :type status: int
        :type message: string
        :rtype: void

        Used to log output messages to file, which will then be forwarded to ElasticSearch.

        Example Usage:
        self.__logging_wrapper('MPLS-WAN-UTILIZATION', self.__FAIL, 'Some reason for failure.')
        """
        if status == self.__PASS:
            status_string = 'PASS'
        elif status == self.__FAIL:
            status_string = 'FAIL'
        else:
            status_string = 'INCOMPLETE'

        new_message = '{0} {1} {2} {3}'.format(self.__site.upper(), test_name, status_string, message)
        self.__logger.info(new_message)


    def __set_logger(self):
        """
        :rtype: void

        PRIVATE METHOD:
        Sets up the loggers for debugging and to ElasticSearch.

        Example Usage:
        self.__set_logger()
        """
        # format of:
        # Month Day Year Military_Time PST
        logging.basicConfig(filename='/var/log/elastic/health_check.log', level=logging.INFO, format='%(asctime)s PST %(message)s', datefmt='%b %d %Y %H:%M:%S')
        self.__logger = logging.getLogger('health-check-log')

        # silence the paramiko logger
        paramiko_logger = logging.getLogger('paramiko')
        paramiko_logger.setLevel(logging.CRITICAL)

        # silence the Elasticsearch logger
        elastic_logger = logging.getLogger('elasticsearch')
        elastic_logger.setLevel(logging.CRITICAL)

        # silence the Elasticsearch logger
        elastic_trace_logger = logging.getLogger('elasticsearch.trace')
        elastic_trace_logger.setLevel(logging.CRITICAL)


    def __post_to_elastic(self, doc_type, body):
        """
        :type doc_type: string
        :type body: JSON object
        :rtype: void

        PRIVATE METHOD:
        Used to post output directly to Elasticsearch. The timestamp will be added to the body.

        Example Usage:
        self.__post_to_elastic('traces', trace_output)
        """
        # format the index for later use
        body['@timestamp'] = datetime.datetime.utcnow()

        date = str(datetime.datetime.now())
        revised_date = date[:date.find(' ')].replace('-', '.')
        index = 'netlog-{0}'.format(revised_date)

        # static variable
        NetworkSite.es.index(index=index, doc_type=doc_type, body=body) 



    def __set_vpn_router(self):
        """
        :rtype: void

        PRIVATE METHOD:
        Attempts to connect to the vpn router at a site. First tries vpn-router, then vpn-router-1.

        Example Usage:
        self.__set_vpn_router()
        """
        #special cases
        if (self.__site == 'us02'):
            self.__vpn_router = RouterConnection('cisco_ios', 'dc8-vpn-router')
            return

        # first try just vpn-router
        self.__vpn_router = RouterConnection('cisco_ios', '{0}-vpn-router'.format(self.__site))
        if not self.__vpn_router.is_connected():
            # next try vpn-router-1
            self.__vpn_router = RouterConnection('cisco_ios', '{0}-vpn-router-1'.format(self.__site))

        # vpn-router will still not be connected here if failure


    def __set_mpls_router(self):
        """
        :rtype: void

        PRIVATE METHOD:
        Attempts to connect to the mpls router at a site. First tries mpls-router, then mpls-router-1.

        Example Usage:
        self.__set_mpls_router()
        """
        # first try just mpls-router
        self.__mpls_router = RouterConnection('cisco_ios', '{0}-mpls-router'.format(self.__site))
        if not self.__mpls_router.is_connected():
            # next try mpls-router-1
            self.__mpls_router = RouterConnection('cisco_ios', '{0}-mpls-router-1'.format(self.__site))

        # mpls-router will still not be connected here if failure


    def __set_core_switch(self):
        """
        :rtype: void

        PRIVATE METHOD:
        Attempts to connect to the core switch at a site. First tries core-switch, then core-switch-1.

        Example Usage:
        self.__set_core_switch()
        """
        # special cases
        if (self.__site == 'us02'): 
            self.__core_switch = RouterConnection('cisco_xe', 'dc2-c6807-core')
            return

        # first try just core-switch
        self.__core_switch = RouterConnection('cisco_xe', '{0}-core-switch'.format(self.__site))
        if not self.__core_switch.is_connected():
            # next try core-swith-1
            self.__core_switch = RouterConnection('cisco_xe', '{0}-core-switch-1'.format(self.__site))

        # core switch will still be None here if failure


    def __initialize_latency_table(self):
        """
        :rtype: void

        PRIVATE METHOD:
        Gets data from solarwinds, depending on whether the site is located in the INTL or the US server. Saves the data table in a private variable. Gathers
        the data from the last __NUM_HIST_DAYS.

        Example Usage:
        self.__initialize_latency_table()
        """
        if ('us' in self.__site or 'ca' in self.__site or 'cl' in self.__site or 'netlab' in self.__site):
            # Connect to solarwinds-us database
            try:
                conn = pyodbc.connect('DRIVER=/usr/lib64/libtdsodbc.so.0;SERVER=10.15.84.13;PORT=1433;DATABASE=NetPerfMonUS;UID=SolarWindsOrionDatabaseuser;PWD=fsck16')
            except Exception as e:
                self.__latency_table = None
                return      
        else:
            # Connect to solarwinds-intl database
            try:
                conn = pyodbc.connect('DRIVER=/usr/lib64/libtdsodbc.so.0;SERVER=10.225.16.15;PORT=1433;DATABASE=NetPerfMonInt;UID=SolarWindsOrionDatabaseuser;PWD=fsck16')
            except Exception as e:
                self.__latency_table = None
                return  
        
        cursor = conn.cursor()

        # have to truncate last three decimal figures for the solarwinds database
        check_date = str(datetime.datetime.now() - datetime.timedelta(days=self.__NUM_HIST_DAYS))
        check_date = check_date[:-3]

        if (self.__site == 'us02'):
            site_1 = 'dc2'
            site_2  = 'dc8'
        else:
            site_1 = self.__site
            site_2 = self.__site.upper()

        cursor.execute("""
            Select Cast(Display_Source As nvarchar(250)) as Display_Source,  Cast(Display_Target As nvarchar(250)) as Display_Target, Avg_Round_Trip_Time, RecordTime From ( SELECT  TOP 10000 OperationCurrentStats_VoIPOperationCurrentStats.OperationTypeName AS Operation_Type,
            OperationCurrentStats_VoIPOperationCurrentStats.DisplaySource AS Display_Source,
            OperationCurrentStats_VoIPOperationCurrentStats.DisplayTarget AS Display_Target,
            OperationResults_VoipOperationResults.AvgRoundTripTime AS Avg_Round_Trip_Time,
            OperationResults_VoipOperationResults.RecordTime AS RecordTime

            FROM
            VoIPOperationCurrentStats OperationCurrentStats_VoIPOperationCurrentStats INNER JOIN VoipOperationResults OperationResults_VoipOperationResults ON (OperationCurrentStats_VoIPOperationCurrentStats.VoipOperationInstanceID = OperationResults_VoipOperationResults.VoipOperationInstanceID)


            WHERE OperationResults_VoipOperationResults.RecordTime > '{0}'
            AND
            OperationCurrentStats_VoIPOperationCurrentStats.OperationTypeName = 'ICMP Echo'
            AND OperationResults_VoipOperationResults.AvgRoundTripTime != 0
            AND
            (
            CHARINDEX('{1}', OperationCurrentStats_VoIPOperationCurrentStats.DisplaySource) > 0
            OR CHARINDEX('{2}', OperationCurrentStats_VoIPOperationCurrentStats.DisplaySource) > 0
            )
            ) As r
        """.format(check_date, site_1, site_2))

        # makes everything lowercase
        self.__latency_table = [[entry.lower() if type(entry) == unicode else entry for entry in cell] for cell in cursor.fetchall()]


    def __get_historical_latency(self, source, dest):
        """
        :type source: string
        :type dest: string
        :rtype: float, float

        PRIVATE METHOD:
        Gets historical latency from Solarwinds database, given a source and destination. Returns median, and one std above median.

        Example Usage:
        hist_latency, one_std_above_latency = self.__get_historical_latency(source, dest)
        """
        # if initilize didn't work
        if self.__latency_table == None:
            return None, None

        all_latency_figures = [cell[2] for cell in self.__latency_table if source.lower() in str(cell[0]) and dest.lower() in str(cell[1])]

        # if (len(all_latency_figures) == 0):
        #     # just use the site, could be a disagreement between name in table and name returned by lookup
        #     all_latency_figures = [cell[2] for cell in self.__latency_table if self.__site in str(cell[0]) and dest in str(cell[1])]

        if len(all_latency_figures) == 0:
            return None, None
        else:
            # one std above the median
            median = statistics.median(all_latency_figures)
            
            rounded_median = float('{0:.3f}'.format(median))
            one_std_above = float('{0:.3f}'.format(median + statistics.pstdev(all_latency_figures)))
            return rounded_median, one_std_above


    def __get_exit_interface(self, connect):
        """
        :type connect: RouterConnection
        :rtype: string, boolean

        PRIVATE METHOD:
        Used to get the exit interface of the device for calculation of utilization. Returns a string and boolean
        that represents whether or not the exit interface was successfully found.

        EXAMPLE USAGE:
        interface = self.__get_exit_interface(connect)
        """
        output = connect.execute_short('sh ip int brief | i up.+up')
        if output == None:
            return 'Command \'sh ip int brief | i up.+up\' failed for {0}.'.format(connect.get_name()), False

        all_interfaces = re.findall(r'(\S+)\s+(\d+[.]\d+[.]\d+[.]\d+).+up\s+up', output)

        # filters all of the interfaces into those that can actually be used
        possible_interfaces = [interface for interface in all_interfaces if not interface[1].startswith('10.') and not ('Tunnel' in interface[0])]

        if len(possible_interfaces) == 0:
            return 'No valid exit interface (non-Tunnel, non-10-net IP) found for {0}.'.format(connect.get_name()), False
        else:
            return_interface = possible_interfaces[0][0]
            period_index = return_interface.find('.')
            if (period_index != -1): 
                return_interface = return_interface[:period_index]

            return return_interface, True


    def __get_bandwidth_nums(self, connect, exit_interface):
        """
        :type connect: RouterConnection
        :type exit_interface: string
        :rtype: string or List[float]

        PRIVATE METHOD:
        Gets the bandwidth numbers of a given device by running a show command. Returns a string with the corresponding
        error if the command fails and a list of the actual numbers if successful.

        Example Usage:
        info = self.__get_bandwidth_nums(connect, exit_interface) 
        """
        output = connect.execute_short('sh int {0} | i bits/sec|BW'.format(exit_interface))
        if output == None:
            return 'Command \'sh int {0} | i bits/sec|BW\' failed for {1}'.format(exit_interface, connect.get_name())

        bandwidth = parse_info(r'BW (\d+)', output, 1)
        inbps = parse_info(r'input rate (\d+)', output, 1)
        outbps = parse_info(r'output rate (\d+)', output, 1)

        if len(bandwidth) == 0 or len(inbps) == 0 or len(outbps) == 0:
            return 'Output of command \'sh int {0} | i bits/sec|BW\' did not include BW, input, or output rate for {1}.'.format(exit_interface, connect.get_name())
        else:
            return [float(bandwidth[0]), float(inbps[0]), float(outbps[0])]


    def __has_acceptable_utilization(self, connect, is_mpls, test_name):
        """
        :type connect: RouterConnection
        :type is_mpls: boolean
        :type test_name: string
        :rtype: Dict

        PRIVATE METHOD:
        Calculates the utilization figures for the router and returns whether they are acceptable (below UTILIZATION_THRESHOLD).

        Example Usage:
        info = self.__has_acceptable_utilization(connect, True, 'MPLS-WAN-UTILIZATION')
        """
        hostname = connect.get_name()

        exit_interface, exit_interface_success = self.__get_exit_interface(connect)
        if not exit_interface_success:
            self.__logging_wrapper(test_name, self.__INCOMPLETE, exit_interface)
            return {'status': self.__INCOMPLETE, 'message': exit_interface, 'router': hostname}

        bandwidth_info = self.__get_bandwidth_nums(connect, exit_interface)
        if type(bandwidth_info) == str:
            self.__logging_wrapper(test_name, self.__INCOMPLETE, bandwidth_info)
            return {'status': self.__INCOMPLETE, 'message': bandwidth_info, 'router': hostname, 'exit_interface': exit_interface}

        bandwidth, inbps, outbps = bandwidth_info

        # convert from Kbits/sec to bits/sec and then accounts for overhead
        bandwidth *= self.__BIT_CONVERSION
        if is_mpls:
            bandwidth *= self.__MPLS_UTILIZATION_CORRECTION

        # converted from decimal to percent
        in_utilization = float('{0:.3f}'.format(inbps / bandwidth * self.__PERCENTAGE_CONVERSION))
        out_utilization = float('{0:.3f}'.format(outbps / bandwidth * self.__PERCENTAGE_CONVERSION))

        output_info = {'router': hostname, 'exit_interface': exit_interface, 'in_utilization': in_utilization, 'out_utilization': out_utilization}

        if (in_utilization > self.__UTILIZATION_THRESHOLD or out_utilization > self.__UTILIZATION_THRESHOLD):
            self.__logging_wrapper(test_name, self.__FAIL, 'Exceeded maximum utilization of {0}%.'.format(self.__UTILIZATION_THRESHOLD))
            output_info.update({'status': self.__FAIL, 'message': 'Exceeded maximum utilization of {0}%.'.format(self.__UTILIZATION_THRESHOLD)})
        else:
            self.__logging_wrapper(test_name, self.__PASS, 'Below maximum utilization of {0}%.'.format(self.__UTILIZATION_THRESHOLD))
            output_info.update({'status': self.__PASS, 'message': 'Below maximum utilization of {0}%.'.format(self.__UTILIZATION_THRESHOLD)})

        return output_info


    def __test_VPN_BGP(self):
        """
        :rtype: Dict

        PRIVATE METHOD:
        Tests to see that the BGP protocol for a vpn router is working properly. Checks to see that the three main VPN hubs are active -
        10.227.4.255, 10.227.5.255 and 10.227.6.255. Checks to see that the state column is a number and greater than the defined threshold,
        which shows that the given neighbor is up.

        Example Usage:
        info = self.__test_VPN_BGP()
        """
        hostname = self.__vpn_router.get_name()
        vpn_source = self.__vpn_router.get_source()

        if not vpn_source:
            output = self.__vpn_router.execute_short('show ip bgp summary')
            if output != None:
                all_info = re.findall(r'(\d+[.]\d+[.]\d+[.]\d+)\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+(\S+)', output)

                # if able to SSH, then it should count as a success
                return {'router': hostname, 'status': self.__PASS, 'neighbors': [{'neighbor_ip': entry[0], 'state_pfxrcd': entry[1], 'status': self.__PASS, 'message': 'No VPN source, SSH counts as success.'} for entry in all_info],
                    'message': 'No VPN source, SSH counts as success.'}
            else:
                return {'router': hostname, 'status': self.__INCOMPLETE, 'message': 'Command \'show ip bgp summary\' failed for {0}.'.format(hostname)}
        else:
            output = self.__vpn_router.execute_short('show ip bgp summary | i 10.227')
            if output == None:
                return {'router': hostname, 'status': self.__INCOMPLETE, 'message': 'Command \'show ip bgp summary | i 10.227\' failed for {0}.'.format(hostname)}

            # VPN hubs don't need themselves as neighbors
            if (hostname == 'dc8-vpn-router'):
                ip_list = [5, 6]
            elif (hostname == 'mdc-vpn-router'):
                ip_list = [4, 6]
            elif (hostname == 'jp01-vpn-router'):
                ip_list = [4, 5]
            else:
                ip_list = [4, 5, 6]

            output_info = {'router': hostname, 'neighbors': [], 'status': self.__PASS}
            for num in ip_list: # loops through the three VPN hubs (10.227.4.255, 10.227.5.255, 10.227.6.255)
                vpn_hub = '10.227.{0}.255'.format(num)

                if (vpn_hub not in output):
                    output_info['neighbors'].append({'neighbor_ip': vpn_hub, 'status': self.__FAIL, 'message': 'Missing VPN hub.'})
                    output_info['status'] = self.__FAIL
                    continue

                state = parse_info(r'{0}\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+(\S+)'.format(vpn_hub), output, 1)[0]

                # checks up down status, returns False if it is not a number
                if (not state.isdigit() or int(state) < self.__BGP_THRESHOLD):
                    output_info['neighbors'].append({'neighbor_ip': vpn_hub, 'state_pfxrcd': state, 'status': self.__FAIL, 'message': 'Insufficient state (less than {0}).'.format(self.__BGP_THRESHOLD)})
                    output_info['status'] = self.__FAIL
                else:
                    output_info['neighbors'].append({'neighbor_ip': vpn_hub, 'state_pfxrcd': state, 'status': self.__PASS, 'message': 'Sufficient state (at least {0}).'.format(self.__BGP_THRESHOLD)})

            if output_info['status'] == self.__FAIL:
                output_info['message'] = 'Missing VPN hub(s) or VPN hub(s) have insufficient state.'
            else:
                output_info['message'] = 'VPN hubs are all up and have sufficient states.'


            return output_info


    def __test_MPLS_BGP(self):
        """
        :rtype: Dict

        PRIVATE METHOD:
        Tests to see that the BGP protocol for a MPLS router is working properly. Checks to see that at least one non 10-net neighbors is up,
        does so by looking at the state column and seeing whether it is a number and that the number exceeds the constant threshold.

        Example Usage:
        info = self.__test_MPLS_BGP()
        """
        hostname = self.__mpls_router.get_name()
        output = self.__mpls_router.execute_short('show ip bgp summary | i .+\..+\..+\..+')
        if output == None:
            return {'router': hostname, 'status': self.__INCOMPLETE, 'message': 'Command \'show ip bgp summary | i .+\..+\..+\..+\' failed for {0}.'.format(hostname)}

        # find all non-10 net neighbors
        format_string = r'(?![*]10[.]|10[.]|0[.]|[.])(\d+[.]\d+[.]\d+[.]\d+)\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+(\S+)'
        match = re.findall(format_string, output)

        if not match:
            # else, use a different command
            output = self.__mpls_router.execute_short('show ip bgp vpnv4 vrf MPLS summary | i .+\..+\..+\..+')
            if output == None:
                return {'router': hostname, 'status': self.__INCOMPLETE, 'message': 'Command \'show ip bgp vpnv4 vrf MPLS summary | i .+\..+\..+\..+\' failed for {0}.'.format(hostname)}
            
            match = re.findall(format_string, output)

        if not match:
            return {'router': hostname, 'status': self.__FAIL, 'message': 'Failed to find non 10-net neighbor.'}

        # checks to see that at least one of the non 10-net neighbors is up
        for entry in match:
            ip_address = entry[0]
            state = entry[1]
            if (state.isdigit() and int(state) >= self.__BGP_THRESHOLD):
                return {'router': hostname, 'neighbors': [{'neighbor_ip': ip_address, 'state_pfxrcd': state, 'status': self.__PASS, 'message': 'Sufficient state (at least {0}).'.format(self.__BGP_THRESHOLD)}], 
                    'status': self.__PASS, 'message': 'Neighbor IP has sufficient state (at least {0}).'.format(self.__BGP_THRESHOLD)}

        # no non 10 net neighbors are up or have sufficient state, prints out all the information
        return {'router': hostname, 'status': self.__FAIL, 'message': 'No non-10 net neighbors are up or have sufficient state (at least {0}).'.format(self.__BGP_THRESHOLD),
            'neighbors': [{'neighbor_ip': entry[0], 'state_pfxrcd': entry[1], 'status': self.__FAIL, 'message': 'Insufficient state (less than {0}).'.format(self.__BGP_THRESHOLD)} for entry in match]}


    def __get_error_counts(self, interface, connect):
        """
        :type interface: string
        :type connect: RouterConnection
        :rtype: Dict

        PUBLIC METHOD:
        Executes a show interface command for the given interface and looks at total output drops, input errors, CRC, output errors, interface resets, and collisions.
        Currently flags any command failures or non-zero error counts. Clears the counters if there are errors detected.
        
        Example Usage:
        errors = self.__get_error_counts(interface, connect)
        """
        hostname = connect.get_name()

        # gets main interface if needed
        period_index = interface.find('.')
        if (period_index != -1): 
            interface = interface[:period_index]

        output_info = {'router': hostname, 'interface': interface}

        # gets the errors that need to be checked
        output = connect.execute_short('show interface {0} | i output drops|errors|Description|Last clearing'.format(interface))
        if output == None:
            output_info.update({'status': self.__INCOMPLETE, 'message': 'Command \'show interface {0} | i output drops|errors\' failed for {1}.'.format(interface, hostname)})

        # grab the description
        description_info = parse_info(r'Description: ([^\n]+)', output, 1)
        if len(description_info) != 0:
            output_info['description'] = description_info[0]

        # grab last cleared
        last_cleared = parse_info(r'Last clearing of "show interface" counters (\S+)', output, 1)
        if len(last_cleared) != 0:
            output_info['last_cleared'] = last_cleared[0]


        if ('Total output drops' not in output or 'output errors' not in output or 'input errors' not in output):
            output_info.update({'status': self.__INCOMPLETE, 'message': 'Command \'show interface {0} | i output drops|errors\' did not show one of output drops, output errors, or input errors for {1}.'.format(interface, hostname)})
            return output_info

        # gets total drops, input errors, and CRC
        num_total_drops = int(parse_info(r'Total output drops: (\d+)', output, 1)[0])

        info = parse_info(r'(\d+) input errors, (\d+) CRC', output, 2)
        num_in_errors = int(info[0])
        num_CRC = int(info[1])

        # parses using different string, as collisions is not found in all interface summaries
        if ('collisions' in output):
            info = parse_info(r'(\d+) output errors, (\d+) collisions, (\d+) interface resets', output, 3)
            num_out_errors = int(info[0])
            num_collisions = int(info[1])
            num_resets = int(info[2])
        else:
            info = parse_info(r'(\d+) output errors, (\d+) interface resets', output, 2)
            num_out_errors = int(info[0])
            num_resets = int(info[1])
            num_collisions = None

        # fills in rows and clears the counters if needed
        output_info.update({'num_in_errors': num_in_errors, 'num_CRC': num_CRC, 'num_out_errors': num_out_errors, 'num_total_drops': num_total_drops, 'num_resets': num_resets})
        if num_collisions != None:
            output_info['num_collisions'] = num_collisions

        if (num_in_errors > 0 or num_CRC > 0 or num_out_errors > 0 or (num_collisions != None and num_collisions > 0) or num_resets > 0 or num_total_drops > 0):
            output = connect.execute_short('clear counters {0}'.format(interface), expect_string='Clear "show interface" counters on this interface')
            if output != None and 'Clear "show interface" counters on this interface' in output:
                # send confirmation
                connect.execute_short('')

            output_info.update({'status': self.__FAIL, 'message': 'Non-zero error counts.'})
        else:
            output_info.update({'status': self.__PASS, 'message': 'No found errors.'})
        
        return output_info


    def __get_ping_latency(self, output):
        """
        :type output: string
        :rtype: List[int]

        PRIVATE METHOD:
        Parses output for ping success percentage. Uses the parse_info helper function to pull all of the data from the output.
        Returns the data in a list with the first element as the percent and the second as the latency.

        Example Usage:
        info = self.__get_ping_latency(output)
        """
        percent_info = parse_info(r'Success rate is (\d+) percent [(]\d+/\d+[)]', output, 1)
        percent = int(percent_info[0]) if len(percent_info) != 0 else None
        latency_info = parse_info(r'round-trip min/avg/max = \d+/(\d+)/\d+ ms', output, 1)
        latency = int(latency_info[0]) if len(latency_info) != 0 else None

        return [percent, latency]


    def __parallel_connect_helper(self, ip, device_type, all_connections, mutex):
        """
        :type ip: string
        :type device_type: string
        :type all_connections: List[RouterConnection]
        :type mutex: threading.Lock
        :rtype: void

        PRIVATE METHOD:
        Creates a new ssh connection and adds it to the given all_connections list. Used when connecting to multiple sessions at once
        in multiple threads. If the connection fails, then the object is not added to the list.

        Example Usage:
        thread = threading.Thread(target=self.__parallel_connect_helper, args=(ip, device_type, all_connections, mutex))
        """
        # simply appends the new connect object to the list that is passed in
        new_connect = RouterConnection(device_type, ip)
        if new_connect.is_connected():
            # use mutex to protect shared list
            with mutex:
                all_connections.append(new_connect)


    def __get_multiple_connections(self, ip, device_type):
        """
        :type ip: string
        :type device_type: string
        :rtype: List[RouterConnection]

        PRIVATE METHOD:
        Uses threading to connect to multiple devices simultaneously. Given the ip and device_type, returns up to MAX_EXTRA_CONNECTIONS amount of device connections
        stored in a list. Returns the list of all successful connections.

        Example Usage:
        connections = self.__get_multiple_connections(ip, device_type)
        """
        # list used to store the threads and connections
        threads = []
        all_connections = []
        mutex = threading.Lock()

        # creates connections
        for i in xrange(self.__MAX_EXTRA_CONNECTIONS):
            t = threading.Thread(target=self.__parallel_connect_helper, args=(ip, device_type, all_connections, mutex))
            threads.append(t)
            t.start()

        # wait for threads to finish
        for t in threads:
            t.join()

        return all_connections


    def __create_message_helper(self, connect, dest, percent, latency, all_messages, output_info):
        """
        :type connect: RouterConnection
        :type dest: string
        :type percent: int
        :type latency: int
        :type all_messages: List[string]
        :type output_info: Dict
        :rtype: void

        PRIVATE METHOD:
        Used in create_message_object. Taken out of the function to reduce redundancy in code, as this same functionality is needed
        for ping_helper_VPN.

        Example Usage:
        self.__create_message_helper(connect, dest, percent, latency, all_messages, output_info)
        """
        historical_latency, one_std_above_latency = self.__get_historical_latency(connect.get_name(), dest)

        output_info['percent'] = percent
        if latency != None:
            output_info['latency'] = latency

        if historical_latency != None:
            output_info.update({'hist_latency': historical_latency, 'comp_latency': one_std_above_latency})

        if percent < self.__PING_THRESHOLD:
            all_messages.append('Ping success less than {0}%.'.format(self.__PING_THRESHOLD))
            output_info['status'] = self.__FAIL
        
        if one_std_above_latency != None and latency != None and latency > one_std_above_latency:
            all_messages.append('Real-time latency is more than one std. above historical median.')
            output_info['status'] = self.__FAIL

        overall_message = ' '.join(all_messages)
        if overall_message != '':
            output_info['message'] = overall_message
        else:
            output_info['message'] = 'All ping numbers are acceptable.'



    def __create_message_object(self, connect, dest, info):
        """
        :type connect: RouterConnection
        :type dest: string
        :type info: List[int]
        :rtype: Dict

        PRIVATE METHOD:
        Helper method that is used to help create output dictionary for pings. Calls __create_info_object as a helper
        and then sets the message of the output.

        Example Usage:
        info = self.__create_message_object(connect, dest, info)
        """
        percent = info[0]
        latency = info[1]

        # create output object
        output_info = {'source': connect.get_name(), 'dest': dest, 'status': self.__PASS}
        all_messages = []

        self.__create_message_helper(connect, dest, percent, latency, all_messages, output_info)

        return output_info



    def __ping_helper_WAN(self, connect, all_ip_info, all_info, ip_mutex, info_mutex):
        """
        :type connect: RouterConnection
        :type all_ip_info: List(Dict)
        :type all_info: Dict
        :type ip_mutex: threading.Lock
        :type info_mutex: threading.Lock
        :rtype: void

        PRIVATE METHOD:
        Helper function used in parallel threading for multiple pings. Loops continuously, popping off an address from the list of all addresses until
        none are left, at which point the loop breaks. After grabbing the IP, this function runs a ping to the specified location and appends an output dictionary
        to the all_info dictionary, which is changed by reference.

        Example Usage:
        thread = threading.Thread(target=self.__ping_helper_WAN, args=(connect, all_ips, all_ip_names, all_info, ip_mutex, info_mutex))
        """
        while True:
            with ip_mutex:
                if len(all_ip_info) == 0:
                    break
                else:
                    new_info = all_ip_info.pop()
                    ip = new_info['ip']
                    name = new_info['name']

            output = connect.execute('ping {0} repeat {1}'.format(ip, self.__PING_AMOUNT))
            if output != None:
                info = self.__get_ping_latency(output)

            # check if the results are viable
            if output == None or (info[0] == None and info[1] == None):
                if output == None:
                    message = 'Command \'ping {0} repeat {1}\' failed for {2}.'.format(ip, self.__PING_AMOUNT, connect.get_name())
                else:
                    message = 'Output of command \'ping {0} repeat {1}\' did not include percent success or latency for {2}.'.format(ip, self.__PING_AMOUNT, connect.get_name())

                with info_mutex:
                    all_info['pings'].append({'status': self.__INCOMPLETE, 'source': connect.get_name(), 'dest': name, 'message': message})
                    if all_info['status'] == self.__PASS:
                        all_info['status'] = self.__INCOMPLETE

                continue        

            output_info = self.__create_message_object(connect, name, info)

            # error

            if output_info['status'] == self.__FAIL:
                with info_mutex:
                    all_info['status'] = self.__FAIL

            with info_mutex:
                all_info['pings'].append(output_info)



    def __ping_helper_VPN(self, connect, all_ip_info, all_info, ip_mutex, info_mutex):
        """
        :type connect: RouterConnection
        :type all_ip_info: List(Dict)
        :type all_info: Dict
        :type ip_mutex: threading.Lock
        :type info_mutex: threading.Lock

        PRIVATE METHOD:
        Helper function used in parallel threading for multiple pings and traces. Loops continuously, popping off an address from the list of all addresses until
        none are left, at which point the loop breaks. After grabbing the IP, this function runs a ping to the specified location and appends an output dictionary
        to the all_info dictionary, which is changed by reference.

        Example Usage:
        thread = threading.Thread(target=self.__ping_helper_VPN, args=(connect, all_ips, all_ip_names, all_info, ip_mutex, info_mutex))
        """
        prompt = connect.get_prompt()
        while True:
            with ip_mutex:
                if len(all_ip_info) == 0:
                    break
                else:
                    new_info = all_ip_info.pop()
                    ip = new_info['ip']
                    name = new_info['name']

            # initialize the output info dictionary
            output_info = {'status': self.__PASS, 'source': connect.get_name(), 'dest': '{0} ({1})'.format(name, ip)}
            all_messages = []

            # first deal with trace
            trace_output = self.__trace_numeric(connect, ip, self.__MAX_HOPS)
            if trace_output != None:
                output_info['trace_output'] = trace_output

                # post to elastic
                self.__post_to_elastic('traces', {'trace_source': connect.get_name(), 'trace_dest': '{0} ({1})'.format(name, ip), 'trace_output': trace_output})
            else:
                all_messages.append('Numeric trace failed.')
                output_info['status'] = self.__FAIL

            # then look at the ping results
            info = self.__ping_test(connect, ip)
            if type(info) == str:
                all_messages.append(info)

                overall_message = ' '.join(all_messages)
                output_info['message'] = overall_message
                if output_info['status'] == self.__PASS:
                    output_info['status'] = self.__INCOMPLETE

                # append and continue
                with info_mutex:
                    if all_info['status'] == self.__PASS and output_info['status'] == self.__INCOMPLETE:
                        all_info['status'] = self.__INCOMPLETE
                    all_info['pings'].append(output_info)

                continue
            
            percent = info[0]
            latency = info[1]

            self.__create_message_helper(connect, ip, percent, latency, all_messages, output_info)

            # error
            if output_info['status'] == self.__FAIL:
                with info_mutex:
                    all_info['status'] = self.__FAIL  

            with info_mutex:
                all_info['pings'].append(output_info)



    def __run_parallel_pings(self, all_switch_connects, all_ip_info, thread_helper, test_name):
        """
        :type all_switch_connects: List[RouterConnection]
        :type all_ip_info: List(Dict)
        :type thread_helper: function
        :type test_name: string
        :rtype: Dict

        PRIVATE METHOD:
        Runs multiple threads to ping numerous locations at the same time. Exits from all but the last connection at the end of the function.
        This is used for both check_vpn_ping_trace and check_core_switch_ping functions.

        Example Usage:
        info = self.__run_parallel_pings(all_switch_connects, all_ip_info, self.__ping_helper_WAN, 'CORE-SWITCH-PING')
        """
        threads = []

        all_info = {'router': all_switch_connects[0].get_name(), 'pings': [], 'status': self.__PASS}

        ip_mutex = threading.Lock()
        info_mutex = threading.Lock()

        for connect in all_switch_connects:
            t = threading.Thread(target=thread_helper, args=(connect, all_ip_info, all_info, ip_mutex, info_mutex))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # disconnects from all but last object
        for connect in all_switch_connects[:-1]:
            connect.disconnect()

        if all_info['status'] == self.__PASS:
            all_info['message'] = 'All sets of pings were successful.'
        elif all_info['status'] == self.__FAIL:
            all_info['message'] = 'At least one set of pings had unacceptable percent success or latency.'
        else:
            all_info['message'] = 'At least one set of pings did not complete.'

        self.__logging_wrapper(test_name, all_info['status'], all_info['message'])

        return all_info


    def __trace_numeric(self, connect, dest, max_ttl):
        """
        :type connect: RouterConnection
        :type dest: string
        :type max_ttl: int
        :rtype: string

        PRIVATE METHOD:
        Sends commands to use numeric version of trace. Uses a variety of approaches, first attemtping to use the numeric inline command, then send parameters line by line,
        and then finally just using a normal trace. Waits up to max_ttl number of hops.

        Example Usage:
        output = self.__trace_numeric(connect, dest, 30)
        """
        prompt = connect.get_prompt()

        source = connect.get_source()
        source_str = ' source {0} '.format(source) if source else ''

        # used when tracing using vrf INET / DMVPN from a particular source
        hostname = connect.get_name()
        if (hostname == 'dc8-vpn-router'):
            vrf_str = ' vrf INET '
        else:
            vrf_str = ' vrf DMVPN ' if source and hostname != 'mdc-vpn-router' else ''

        # first, try numeric
        output = connect.execute('trace {0} {1} ttl 1 {2} numeric {3}'.format(vrf_str, dest, max_ttl, source_str))

        if (output == None or 'Invalid' in output):
            output = connect.execute_short('trace {0}'.format(vrf_str), expect_string=r'Protocol \[ip\]:|Incomplete command|{0}'.format(prompt))

            if (output == 'Protocol [ip]: '):
                while (output != 'Loose, Strict, Record, Timestamp, Verbose[none]: '):
                    if (output == 'Target IP address: '):
                        output = connect.execute_short(dest, expect_string=':')
                    elif (output == 'Source address: '):
                        output = connect.execute_short(source, expect_string=':') if source else connect.execute_short('', expect_string=':')
                    elif (output == 'Numeric display [n]: '):
                        output = connect.execute_short('y', expect_string=':')
                    elif (output == 'Maximum Time to Live [30]: '):
                        output = connect.execute_short(str(max_ttl), expect_string=':')                        
                    else:
                        output = connect.execute_short('', expect_string=':')    

                output = connect.execute('', expect_string=prompt)

        # get rid of header on output, two possible formats
        if output != None:
            index = output.find('  1 ')
            if (index == -1): 
                index = output.find(' 1 ')
            if (index != -1):
                output = output[index:]

        return output


    def __check_out_path(self, trace_address):
        """
        :type trace_address: string
        :rtype: Dict

        PRIVATE METHOD:
        Checks to see that the traceroute command takes an MPLS route while accessing intranet.  If the core switch address is found in HQ, then the destination trace address is chosen
        to be outside of HQ. else, the trace address can be chosen as one within the subnets of HQ. The function checks to see that the first hop of the path has 46 as its last octet in
        the ip address, signaling that the path taken is MPLS and not VPN. Also checks whethe the last octet has 30 as its last octet, which is indicative of a VPN path.
        As a last resort, can also check the second hop to see whether it is 10.227.4.255, 10.227.5.255, or 10.227.6.255, which shows that it is taking a VPN path. Checks the hostname as well for 'mpls'
        or 'vpn'.

        Example Usage:
        info = self.__check_out_path(trace_address)
        """
        core_switch_name = self.__core_switch.get_name() 
        output_info = {'direction': 'outbound', 'source': core_switch_name, 'dest': trace_address}

        output = self.__trace_numeric(self.__core_switch, trace_address, 1)

        if output == None:
            output_info.update({'status': self.__INCOMPLETE, 'message': 'Numeric trace to {0} failed for {1}.'.format(trace_address, core_switch_name)})
            return output_info

        info = parse_info(r'1\s+(?:\S+\s+)?(\d+[.]\d+[.]\d+[.]\d+)', output, 1)
        if len(info) == 0:
            output_info.update({'status': self.__INCOMPLETE, 'message': 'No IP information in numeric trace to {0} for {1}.'.format(trace_address, core_switch_name)})
            return output_info
            
        first_hop_ip = info[0]
        last_octet = first_hop_ip[-3:]

        # initial value for hostname
        hostname = get_hostname_from_ip(first_hop_ip)

        if hostname != None:
            output_info['hop_info'] = '{0} ({1})'.format(hostname, first_hop_ip)
        else:
            output_info['hop_info'] = first_hop_ip

        if ((hostname != None and 'mpls' in hostname) or last_octet == '.46'):
            output_info.update({'status': self.__PASS, 'message': 'First hop in trace is MPLS router.'})
        else:
            output_info.update({'status': self.__FAIL, 'message': 'First hop in trace is not MPLS router.'})

        return output_info


    def __check_in_path(self, cswitch_ip):
        """
        :type cswitch_ip: string
        :rtype: Dict

        PRIVATE METHOD:
        Checks to see that the path from another core switch to the given core switch also takes a MPLS path. Connects to the network-script server and then traces to the
        given ip. Looks for the ip 10.227.4.*, 10.227.5.*, or 10.227.6.* in the path, where * can be any number 0-255, which signifies that the path being taken is a VPN path.

        Example Usage:
        info = self.__check_in_path(self, cswitch_ip)
        """
        # set up another connection to the network-script server
        client = paramiko.client.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            client.connect(hostname='network-script', username=self.__USERNAME, password=self.__PASSWORD)
        except:
            return {'status': self.__INCOMPLETE, 'direction': 'inbound', 'message': 'Failed to connect to network-script using paramiko library for inbound trace.'}

        stdin, stdout, stderr = client.exec_command('traceroute {0} -n'.format(cswitch_ip))
        output = stdout.read()
        output = output[output.find(' 1  '):]      

        client.close()

        ip_info = parse_info(r'(10[.]227[.][456][.]\d+)', output, 1)

        output_info = {'direction': 'inbound', 'source': 'network-script (10.15.210.36)', 'dest': self.__core_switch.get_name()}
        if len(ip_info) != 0: # is vpn
            hub_ip = ip_info[0]
            output_info.update({'status': self.__FAIL, 'message': 'Trace uses VPN hub.', 'hop_info': hub_ip})
        else: # is mpls
            output_info.update({'status': self.__PASS, 'message': 'Trace does not use VPN hub.'})
        
        return output_info


    def __is_vrf(self, connect):
        """
        :type connect: RouterConnection
        :rtype: boolean

        PRIVATE METHOD:
        Used to get whether the device is vrf. Returns a string error if failed, and a boolean if succeeded.

        EXAMPLE USAGE:
        is_vrf = self.__is_vrf(connect)
        """
        # ext and int found, vpn router is NON-VRF
        output = connect.execute_short('show cdp neighbor | i -int|-ext')
        if output == None:
            return 'Command \'show cdp neighbor | i -int|-ext\' failed for {0}.'.format(connect.get_name())

        return not '-ext' in output or not '-int' in output


    def __get_PE_IP(self, connect):
        """
        :type connect: RouterConnection
        :rtype: string, boolean

        PRIVATE METHOD:
        Attempts to find the PE IP for the given connection. Returns a string and a boolean representing the PE IP address if successful, and 
        a string error if not.

        Example Usage:
        pe_ip = self.__get_PE_IP(connect)
        """
        # special sites
        hostname = connect.get_name()
        if (hostname == 'mdc-vpn-router' or hostname == 'jp01-vpn-router' or hostname == 'indc-vpn-router'):
            output = self.__trace_numeric(connect, '198.182.41.251', self.__MAX_HOPS)
            if output == None:
                return 'Numeric trace to 198.182.41.251 failed for {0}.'.format(hostname), False

            # looks for non 10-net, non 198.182-net IP
            format_string = r'(?! 10[.]| 198[.]182[.]) (\d+[.]\d+[.]\d+[.]\d+)'
            info = parse_info(format_string, output, 1)
            if len(info) != 0:
                return info[0], True
            else:
                return 'Output of numeric trace to 198.182.41.251 did not include non-10-net or non-198.182-net IP for {0}.'.format(hostname), False
        elif (hostname == 'dc8-vpn-router'):
            output = connect.execute_short('sh ip bgp vpnv4 vrf INET 0.0.0.0')
            if output == None:
                return 'Command \'sh ip bgp vpnv4 vrf INET 0.0.0.0\' failed for dc8-vpn-router.', False
            else:
                info = parse_info(r'(\d+[.]\d+[.]\d+[.]\d+).+\n.+best', output, 1, find_string='Refresh')
                if len(info) != 0:
                    return info[0], True
                else:
                    return 'Output of command \'sh ip bgp vpnv4 vrf INET 0.0.0.0\' did not include IP for dc8-vpn-router.', False

        output = connect.execute_short('show run | i 0.0.0.0 0.0.0.0')
        if output == None:
            return 'Command \'show run | i 0.0.0.0 0.0.0.0\' failed for {0}.'.format(hostname), False

        # uses different commands depending on the vrf nature of the router, returns False if there is any packet loss
        is_vrf = self.__is_vrf(connect)
        if type(is_vrf) == str:
            return is_vrf, False

        if not is_vrf:
            info = parse_info(r'ip route 0\.0\.0\.0 0\.0\.0\.0 (\d+[.]\d+[.]\d+[.]\d+)', output, 1)
        else:
            info = parse_info(r'ip route vrf DMVPN 0\.0\.0\.0 0\.0\.0\.0 (\d+[.]\d+[.]\d+[.]\d+)', output, 1)

        # no PE IP
        if (len(info) == 0):
            return 'Output of command \'show run | i 0.0.0.0 0.0.0.0\' did not include {0} IP for {1}.'.format('vrf' if is_vrf else 'non-vrf', hostname), False

        ip = info[0]
        if (not ip.startswith('10.') and not ipaddress.ip_address(ip) in ipaddress.ip_network(u'198.182.32.0/19')):
            return ip, True
        else:
            return 'Found IP {0} was either 10-net or in the 198.182.32.0/19 network for {1}.'.format(ip, hostname), False


    def __ping_test(self, connect, dest):
        """
        :type connect: RouterConnection
        :type dest: string
        :rtype: List[int] or string

        PRIVATE METHOD:
        Pings from a given source to a given destination. First sends out a default 5 number of packets to see whether the ping
        command is valid. If the initial command is successful, another PING_AMOUNt packets are sent to collect data.
        Returns the percent success and latency stored in a list if successful, or returns a string error.

        Example Usage:
        info = self.__ping_test(connect, dest)
        """
        source = connect.get_source()

        # sends out 5 packets to quickly check whether the ping will return results
        for amount in [5, self.__PING_AMOUNT]:
            if (source):
                command = 'ping vrf {0} {1} source {2} repeat {3}'.format('DMVPN' if connect.get_name() != 'dc8-vpn-router' else 'INET', dest, source, amount)
            else:
                command = 'ping {0} repeat {1}'.format(dest, amount)

            output = connect.execute(command)
            if output == None:
                return 'Command \'{0}\' failed for {1}.'.format(command, connect.get_name())

            info = self.__get_ping_latency(output)
            if (info[0] == 0):
                return info
            elif info[0] == None and info[1] == None:
                return 'Output of command \'{0}\' did not include percent success or latency for {1}.'.format(command, connect.get_name())

        return info

