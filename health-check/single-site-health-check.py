#!/opt/python-2.7.13/bin/python -u

import sys
import json
from datetime import datetime

sys.path.append('/network/scripts/helper_classes')
from NetworkSite import NetworkSite

# list of all sites
ALL_SITES = ['am04', 'au02', 'be06', 'ca06', 'ca09', 'ca11', 'ca14', 'ca42', 'ch10', 'cl01', 'cn03', 'cn30','cn34', 
    'cn42', 'cn60', 'cn63', 'de02', 'de04', 'de06', 'de11', 'dk01', 'fi01', 'fi03', 'fr01', 'fr02','fr03', 'fr05', 'fr10', 'fr42', 
    'fr65', 'fr7c', 'gb01', 'gb07', 'gb50', 'hk02', 'hu01', 'ie02', 'il01', 'in01', 'in09', 'in17', 'in18', 'in19', 'in23', 'in24', 
    'in25', 'in45', 'in74', 'in7b', 'indc', 'it01','jp01', 'jp02', 'kp01', 'lk01', 'mdc', 'mo90', 'nl20', 'pl01', 'pt01', 
    'pt02', 'ru01', 'ru20', 'se80', 'sg01', 'tw01', 'tw04', 'tw52', 'us01-a', 'us01-b', 'us02', 'us03', 'us04', 'us05', 'us08', 
    'us11','us16', 'us18', 'us20', 'us24', 'us26', 'us27', 'us28', 'us36', 'us38', 'us47', 'us54', 'us59', 'us6a', 'us6d', 'us7m', 
    'us8e', 'us8k', 'us8w', 'us95']


if __name__ == '__main__':
    """
    Version of the health check that asks for user input on the command line. Runs for a single given site.
    """

    # asks for user input
    site = raw_input('Enter site: ')

    print 'Tests:'
    print '1: MPLS WAN Utilization'
    print '2: VPN Internet Utilization'
    print '3: BGP Status'
    print '4: Interface Errors'
    print '5: MPLS Path'
    print '6: Core Switch Ping'
    print '7: VPN Ping HQ'
    print '8: VPN Ping PE IP'
    print '9: VPN Ping Trace'

    tests = raw_input('Enter tests (ie. 1 2 3), press enter to run all: ').split()
    if len(tests) == 0:
        tests = [str(num) for num in range(1, 10)]

    if site in ALL_SITES:

        siteTest = NetworkSite(site)

        all_info = {'site': site, '@timestamp': str(datetime.now())}

        # run the appropriate tests
        if '1' in tests:
            all_info['mpls_wan_utilization'] = siteTest.check_mpls_wan_utilization()
            print 'mpls_wan_utilization'
        if '2' in tests:
            all_info['vpn_internet_utilization'] = siteTest.check_vpn_internet_utilization()
            print 'vpn_internet_utilization'
        if '3' in tests:
            all_info['bgp_status'] = siteTest.check_bgp_status()
            print 'bgp_status'
        if '4' in tests:
            all_info['interface_errors'] = siteTest.check_interface_errors()
            print 'interface_errors'
        if '5' in tests:
            all_info['mpls_path'] = siteTest.check_mpls_path()
            print 'mpls_path'
        if '6' in tests:
            all_info['core_switch_ping'] = siteTest.check_core_switch_ping()
            print 'core_switch_ping'
        if '7' in tests:
            all_info['vpn_ping_hq'] = siteTest.check_vpn_ping_hq()
            print 'vpn_ping_hq'
        if '8' in tests:
            all_info['vpn_ping_pe_ip'] = siteTest.check_vpn_ping_pe_ip()
            print 'vpn_ping_pe_ip'
        if '9' in tests:
            all_info['vpn_ping_trace'] = siteTest.check_vpn_ping_trace()
            print 'vpn_ping_trace'      

        siteTest.finish()

        # for now, just print
        print json.dumps(all_info, indent=4)
    else:
        print '{0} IS NOT A VALID SITE'.format(site)