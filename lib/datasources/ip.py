from lib.datasources.datasource import DataSource
from lib.record import Record

class IP(DataSource):

    def scrape_data(self):
        for ip in self.inventory.get_ips():
            r = Record(ip)
            r.add_attribute('ip', ip)
            self.add_entry(r)

        return self.entries