#!/opt/python-2.7.13/bin/python -u
import sys, traceback
import json
import os
from datetime import datetime
import cgi
import threading
from concurrent.futures import ThreadPoolExecutor, wait

sys.path.append('/network/scripts/helper_classes')
from NetworkSite import NetworkSite

# maximum number of sites to run at a time
MAX_THREADS = 5

# log file
FILENAME = 'all-sites-output.txt'

import time

def health_check_worker(site, print_lock, f):
    """
    Runs all the network health check tests for a single site. Then writes the output to the all sites health check file.
    
    :type site: string
    :type print_lock: threading.Lock()
    :type f: file
    :rtype: void
    """
    with print_lock:
        print site

    try:
        siteTest = NetworkSite(site)

        # create a JSON object with all the results
        all_info = {'site': site, '@timestamp': str(datetime.now())}
        all_info['mpls_wan_utilization'] = siteTest.check_mpls_wan_utilization()
        all_info['vpn_internet_utilization'] = siteTest.check_vpn_internet_utilization()
        all_info['bgp_status'] = siteTest.check_bgp_status()
        all_info['interface_errors'] = siteTest.check_interface_errors()
        all_info['mpls_path'] = siteTest.check_mpls_path()
        all_info['core_switch_ping'] = siteTest.check_core_switch_ping()
        all_info['vpn_ping_hq'] = siteTest.check_vpn_ping_hq()
        all_info['vpn_ping_pe_ip'] = siteTest.check_vpn_ping_pe_ip()
        all_info['vpn_ping_trace'] = siteTest.check_vpn_ping_trace()

        siteTest.finish()

        # write results to file
        with print_lock:
            print 'SUCCESS: {}'.format(site)
            f.write('SUCCESS: {0}\n'.format(site))
            f.write(json.dumps(all_info, indent=4))
            f.write('\n\n')
    except:
        # shouldn't trigger, but just in case
        with print_lock:
            print 'FAILURE: {0}'.format(site)
            traceback.print_exc(file=sys.stdout)
            f.write('FAILURE: {0}\n'.format(site))
            f.write(traceback.format_exc())
            f.write('\n\n')


if __name__ == '__main__':
    """
    Runs the network health check over all sites, using a ThreadPool. Writes the output to a file. This version of the network health check
    does not ask for user input, and is run as a cronjob once a week.
    """

    all_sites = ['us01-a', 'us01-b', 'us02', 'us03', 'us04', 'us05', 'us08',
        'us11','us16', 'us18', 'us20', 'us24', 'us26', 'us27', 'us28', 'us36', 'us38', 'us47', 'us54', 'us59', 'us6a', 'us6d', 'us7m',
        'us8e', 'us8k', 'us8w', 'us95', 'am04', 'au02', 'be06', 'ca06', 'ca09', 'ca11', 'ca14', 'ca42', 'ch10', 'cl01', 'cn03', 'cn30','cn34',
        'cn42', 'cn60', 'cn63', 'de02', 'de04', 'de06', 'de11', 'dk01', 'fi01', 'fi03', 'fr01', 'fr02','fr03', 'fr05', 'fr10', 'fr42',
        'fr65', 'fr7c', 'gb01', 'gb07', 'gb50', 'hk02', 'hu01', 'ie02', 'il01', 'in01', 'in09', 'in17', 'in18', 'in19', 'in23', 'in24',
        'in25', 'in45', 'in74', 'in7b', 'indc', 'it01','jp01', 'jp02', 'kp01', 'lk01', 'mdc', 'mo90', 'nl20', 'pl01', 'pt01',
        'pt02', 'ru01', 'ru20', 'se80', 'sg01', 'tw01', 'tw04', 'tw52']

    # set of threads that can be used
    pool = ThreadPoolExecutor(MAX_THREADS)

    futures = []
    print_lock = threading.Lock()
    with open(FILENAME, 'w') as f:
        for site in all_sites:
            futures.append(pool.submit(health_check_worker, site, print_lock, f))

        # wait for completion of all threads
        wait(futures)