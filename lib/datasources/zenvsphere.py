from datasource import DataSource
from lib.record import Record
from lib.extra.zenoss_api.zenoss import Zenoss
import socket

class ZenVsphere(DataSource):

    def scrape_data(self):
        zenoss = Zenoss(self.connection_options['url'],
                        self.connection_options['username'],
                        self.connection_options['password'],
                        ssl_verify=False)

        vsphere_devices = zenoss.get_devices(device_class='/zport/dmd/Devices/vSphere')['devices']

        for device in vsphere_devices:

            components = zenoss.get_components_by_uid(uid=device['uid'], limit=None)['data']
            vms = [v for v in components if v['class_label'] == 'Virtual Machine']
            hosts = [v for v in components if v['class_label'] == 'Host']

            # map hosts to cluster names
            host_map = dict()
            for h in hosts:
                if 'cluster' in h:
                    host_map[h['uid']] = h['cluster']['name']

            vsphere_data = dict()
            for v in vms:
                ip = self.get_ip(v['guestname'])
                if ip is not None:
                    vsphere_data[ip] = {
                        'guestname': v['guestname']
                    }
                    if 'host' in v and 'name' in v['host']:
                        vsphere_data[ip]['host'] = v['host']['name']

                    if 'host' in v and 'uid' in v['host'] and v['host']['uid'] in host_map:
                        vsphere_data[ip]['cluster'] = host_map[v['host']['uid']]

            for ip in vsphere_data:
                r = Record(ip)
                for name in vsphere_data[ip]:
                    r.add_attribute(name, vsphere_data[ip][name])
                self.add_entry(r)

        return self.entries

    def get_ip(self, vm):
        try_domains = ['campus.ece.cmu.local', 'ece.local.cmu.edu', 'go.ece.cmu.edu',
                       'cit.cmu.edu', 'ece.cmu.edu']
        try:
            result = socket.gethostbyname(vm).strip()
        except socket.gaierror as e:
            # ignore lookup errors
            result = None

        i = 0
        max_index = len(try_domains) - 1
        if vm.endswith('.ECE') or vm.endswith('.CAMPUS'):
            vm = ''.join(vm.split('.')[:-1])
        while result is None and i <= max_index:
            try:
                result = socket.gethostbyname(vm + '.' + try_domains[i]).strip()
            except socket.gaierror as e:
                result = None
            i += 1

        return result