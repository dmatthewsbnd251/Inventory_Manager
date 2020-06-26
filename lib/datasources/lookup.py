from datasource import DataSource
import socket
from lib.record import Record
import re
import logging
logger = logging.getLogger(__name__)

class Lookup(DataSource):

    def scrape_data(self):
        for ip in self.inventory.get_ips():
            logger.debug("Looking up %s" % ip)
            reverse_result = None
            forward_result = None
            try:
                 reverse_result = socket.gethostbyaddr(ip)[0].lower().strip()
            except socket.herror as e:
                # ignore lookups that can't be found
                pass

            if reverse_result is not None:
                try:
                    forward_result = socket.gethostbyname(reverse_result).strip()
                except socket.gaierror as e:
                    # ignore lookup errors
                    pass

            if None not in (forward_result, reverse_result) and ip == forward_result:
                # make sure the result is an fqdn
                if self.is_valid_hostname(reverse_result):
                    logger.debug("Forward and reverse match for %s.  Setting fqdn to %s" % (ip, reverse_result))
                    r = Record(ip)
                    r.add_attribute('fqdn', reverse_result)
                    self.add_entry(r)
                else:
                    logger.debug("The reverse does not look like a valid hostname.  Reverse: %s" % str(reverse_result))
            else:
                logger.debug("Forward and reverse did not match for %s.  Not adding fqdn." % ip)

        return self.entries

    def is_valid_hostname(self, hostname):
        if len(hostname) > 255:
            return False
        if hostname[-1] == ".":
            hostname = hostname[:-1] # strip exactly one dot from the right, if present
        allowed = re.compile("(?!-)[A-Z\d\-_]{1,63}(?<!-)$", re.IGNORECASE)
        return all(allowed.match(x) for x in hostname.split("."))


