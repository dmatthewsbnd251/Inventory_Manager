from datasource import DataSource
from lib.record import Record
from lib.extra.zenoss_api.zenoss import Zenoss

class Zen(DataSource):

    def scrape_data(self):

        zenoss = Zenoss(self.connection_options['url'],
                        self.connection_options['username'],
                        self.connection_options['password'],
                        ssl_verify=False)

        interesting_data = (
            'comments',
            'created_timestamp',
            'description',
            'id',
            'firstSeen',
            'groups',
            'hwManufacturer',
            'location',
            'osModel',
            'osManufacturer',
            'memory',
            'priority',
            'priorityLabel',
            'productionState',
            'productionStateLabel',
            'productionState',
            'serialNumber',
            'status',
            'systems',
            'tagNumber',
            'uid',
            'uptime',
            'severity',
            'uuid',
        )

        interesting_device_class_data = (
            'uid',
            'description',
            'name',
        )
        for device in zenoss.get_devices_detailed():
            if 'data' in device and 'ipAddressString' in device['data'] \
                    and device['data']['ipAddressString'] is not None and len('ipAddressString') > 5:
                r = None
                try:
                    r = Record(device['data']['ipAddressString'])
                except ValueError as e:
                    # ip is probably not set in Zenoss
                    pass
                if r is not None:
                    for data in device['data']:
                        if data in interesting_data:
                            r.add_attribute(str(data), device['data'][data])
                if 'deviceClass' in device['data']:
                    for key in device['data']['deviceClass']:
                        if key in interesting_device_class_data:
                            r.add_attribute('dev_class_info_' + str(key), device['data']['deviceClass'][key])
                    self.add_entry(r)
        return self.entries