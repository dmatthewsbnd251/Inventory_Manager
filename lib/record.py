"""Provides a common format that all data sources must
use to populate records and merge into overall inventory"""

import re

class Record:

    ip = None
    attributes = None

    def __init__(self, ip):

        if self.is_valid_ip(ip):
            self.ip = ip.strip().lower()
        else:
            raise ValueError("%s is not a valid ip" % ip)

        self.attributes = dict()

    def __eq__(self, other):
        return self.ip == other.ip

    def add_attribute(self, attribute_name, attribute_value):
        if isinstance(attribute_name, str):
            self.attributes[attribute_name.lower()] = attribute_value
        else:
            raise ValueError("%s was not a string when adding to %s record.  Attribute names must be in string format"
                             % (attribute_name, self.ip))

    def is_valid_ip(self, ip):
        if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", ip) or \
           re.match(r'([0-9a-fA-F]{0,4}:{1,2}){3,7}[0-9a-fA-F]{0,4}', ip):
            return True
        else:
            return False

    def get_attribute_dict(self):
        return self.attributes