elif(x['service'] == 'ISP'):
        if (x['Device'] == 'sv2'):
            dict = {'in_bps': float(x['in_bps']),
                    'out_bps': float(x['out_bps']),
                    'Device': x['Device'],
                    '@timestamp': x['@timestamp'],
                    'type': x['type'],
                    'Peak': x['Peak'],
                    'service': x['service'],
                    'Circuit Size': 10000,
                    'PerCent': ((x['Peak'] / 10000) * 100)
                    }
            result_final.append(dict)
        elif (x['Device'] == 'indc' or x['Device'] == 'mdc'):
            dict = {'in_bps': float(x['in_bps']),
                    'out_bps': float(x['out_bps']),
                    'Device': x['Device'], '@timestamp': x['@timestamp'], 'type': x['type'], 'Peak': x['Peak'],
                    'service': x['service'], 'Circuit Size': 3000, 'PerCent': ((x['Peak'] / 3000) * 100)
                    }
            result_final.append(dict)
        elif ((x['Device'] == 'am04' or x['Device'] == 'ca06' or x['Device'] == 'in19' or x['Device'] == 'jp01' or
                x['Device'] == 'pt01' or x['Device'] == 'pt02' or x['Device'] == 'us03' or
               x['Device'] == 'us04' or x['Device'] == 'tw52')):
                dict = {'in_bps': float(x['in_bps']),
                        'out_bps': float(x['out_bps']),
                        'Device': x['Device'], '@timestamp': x['@timestamp'], 'type': x['type'], 'Peak': x['Peak'],
                        'service': x['service'], 'Circuit Size': 1000, 'PerCent': ((x['Peak'] / 1000) * 100)
                        }
                result_final.append(dict)
        elif (x['Device'] == 'cn58' or x['Device'] == 'fr65' or x['Device'] == 'il01'):
            dict = {'in_bps': float(x['in_bps']),
                    'out_bps': float(x['out_bps']),
                    'Device': x['Device'], '@timestamp': x['@timestamp'], 'type': x['type'], 'Peak': x['Peak'],
                    'service': x['service'], 'Circuit Size': 500, 'PerCent': ((x['Peak'] / 500) * 100)
                    }
            result_final.append(dict)
        elif (x['Device'] == 'cn42' or x['Device'] == 'gb01'):
            dict = {'in_bps': float(x['in_bps']),
                    'out_bps': float(x['out_bps']),
                    'Device': x['Device'], '@timestamp': x['@timestamp'], 'type': x['type'], 'Peak': x['Peak'],
                    'service': x['service'], 'Circuit Size': 300, 'PerCent': ((x['Peak'] / 300) * 100)
                    }
            result_final.append(dict)
        elif (x['Device'] == 'pl01' or x['Device'] == 'tw01'):
            dict = {'in_bps': float(x['in_bps']),
                    'out_bps': float(x['out_bps']),
                    'Device': x['Device'],
                    '@timestamp': x['@timestamp'],
                    'type': x['type'],
                    'Peak': x['Peak'],
                    'service': x['service'],
                    'Circuit Size': 200,
                    'PerCent': ((x['Peak'] / 200) * 100)
                    }
            result_final.append(dict)
        elif (x['Device'] == 'cl01' or x['Device'] == 'se80' or x['Device'] == 'cn30'):
            dict = {'in_bps': float(x['in_bps']),
                    'out_bps': float(x['out_bps']),
                    'Device': x['Device'], '@timestamp': x['@timestamp'], 'type': x['type'], 'Peak': x['Peak'],
                    'service': x['service'], 'Circuit Size': 100, 'PerCent': ((x['Peak'] / 100) * 100)
                    }
            result_final.append(dict)