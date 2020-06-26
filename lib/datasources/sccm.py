from datasource import DataSource
from lib.record import Record
import csv
import re

class SCCM(DataSource):

    def scrape_data(self):

        with open(self.connection_options['path']) as csvfile:
            readCSV = csv.DictReader(csvfile, delimiter=',')
            data = [r for r in readCSV]
            '''
            [..,
            {'class': 'Client',
             'collection': 'Win 7 x86 Clients',
             'fqdn': 'CMU-946702.GO.ECE.CMU.EDU',
             'ip': '128.2.57.195'}
            ]
            '''
            data_by_ip = {}
            ip4_pattern = re.compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
            for d in data:
                if 'ip' in d and d['ip'] != '':

                    good_ip = False
                    if ' ' in d['ip']:
                        for possible_ip4 in d['ip'].split():
                            if ip4_pattern.match(possible_ip4):
                                d['ip'] = possible_ip4
                                good_ip = True
                                break
                    else:
                        good_ip = True

                    if good_ip:

                        if d['ip'] in data_by_ip:
                            data_by_ip[d['ip']]['class'] = d.get('class', '').lower().strip()
                            data_by_ip[d['ip']]['fqdn'] = d.get('fqdn', '').lower().strip()
                            data_by_ip[d['ip']]['collection'].append(d.get('collection', '').lower().strip())
                        else:
                            data_by_ip[d['ip']] = {
                                'class': d.get('class', '').lower().strip(),
                                'fqdn': d.get('fqdn', '').lower().strip(),
                                'collection': [d.get('collection', '').lower().strip(), ]
                            }

            for ip in data_by_ip:
                entry = Record(ip)
                for key in data_by_ip[ip]:
                    entry.add_attribute(key, data_by_ip[ip][key])
                self.add_entry(entry)

            return self.entries
