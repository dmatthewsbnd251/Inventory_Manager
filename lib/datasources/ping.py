from lib.datasources.datasource import DataSource
from lib.record import Record
import subprocess, os
import logging
logger = logging.getLogger(__name__)

class Ping(DataSource):

    def scrape_data(self):

        for ip in self.inventory.get_ips():
            r = Record(ip)
            logger.debug("Testing ping for %s" % str(ip))
            pingok = self.pingOk(ip, self.connection_options['wait'], self.connection_options['count'])
            if pingok:
                logger.debug("Ping ok for %s" % ip)
            else:
                logger.debug("Ping failed for %s" % ip)
            r.add_attribute('pingable', pingok)
            self.add_entry(r)

        return self.entries

    def pingOk(self, hostname, wait, count):

        ret_code = subprocess.call(['ping', '-c', str(count), '-W', str(wait), hostname],
                                   stdout=open(os.devnull, 'w'),
                                   stderr=open(os.devnull, 'w'))
        if ret_code == 0:
            return True
        else:
            return False