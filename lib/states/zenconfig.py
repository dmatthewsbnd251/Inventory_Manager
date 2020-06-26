"""ZenConfig: implements the State class.
This manages the zenoss state of a record"""

from state import State
from lib.extra.zenoss_api.zenoss import Zenoss
import urllib3
from time import sleep

class ZenConfig(State):

    zenapi = None

    url = None
    username = None
    password = None

    ip = None
    name = None
    exists = None
    priority = None
    productionstate = None
    groups = None
    systems = None
    deviceclass = None
    location = None

    def __init__(self, url, username, password,
                 ip=None,
                 name=None,
                 exists=None,
                 priority=None,
                 productionstate=None,
                 groups=None,
                 systems=None,
                 deviceclass=None,
                 location=None,
                 tries=10,
                 sleep_timer=2,
                 ignore_prodstate_if_exists=True):
        """
        ip: if set indicates settings will be fetched.  This is "get" mode as opposed to "state" mode.
        When ip is passed the values listed below it above should not be set and will be pulled from
        the Zenoss instance.  Only in the state mode can methods that set different states be used.

        no ip: When an ip address is not set, this object exists as a desired state and can be used for
        comparison.
        """

        for val in (url, username, password):
            if not isinstance(val, str):
                raise ValueError("Value was not passed as a string: %s." % str(val))

        if ip is not None:
            for val in (exists, priority, productionstate, groups, systems, deviceclass, location):
                if val is not None:
                    raise ValueError("When ip is passed no other configuration settings should be passed.")
        else:
            if exists is None:
                raise ValueError("When ip is not passed, the minimum of the exists value must be passed.")

            if exists is not None and exists is True:

                if None in (priority, groups, systems, deviceclass, location, name):
                    raise ValueError("All values must be passed when an ip is not set and exists is True except"
                                     "except production state")

                if not isinstance(priority, int):
                    raise ValueError("Priority must be an integer.")

                if not isinstance(productionstate, int) and productionstate is not None:
                    raise ValueError("Production State must be an integer or None.")

                if not isinstance(groups, list):
                    raise ValueError("Groups must be a list")

                if not isinstance(systems, list):
                    raise ValueError("Systems must be a list")

                if not isinstance(deviceclass, basestring):
                    raise ValueError("Device class must be a string.")

                if not isinstance(location, basestring):
                    raise ValueError("Location must be a string.")

                if not isinstance(name, basestring):
                    raise ValueError("Name must be a string.")


        self.url = self.make_unicode_a_string(url)
        self.username = self.make_unicode_a_string(username)
        self.password = self.make_unicode_a_string(password)

        self.ip = self.make_unicode_a_string(ip)
        self.name = self.make_unicode_a_string(name)
        self.exists = exists
        self.priority = priority
        self.productionstate = productionstate
        if groups is not None:
            self.groups = [x for x in groups if len(x) > 0]
        else:
            self.groups = None
        if systems is not None:
            self.systems = [x for x in systems if len(x) > 0]
        else:
            self.systems = None
        self.deviceclass = self.make_unicode_a_string(deviceclass)
        self.location = self.make_unicode_a_string(location)
        self.tries = tries
        self.sleep_timer = sleep_timer
        self.ignore_prodstate_if_exists = ignore_prodstate_if_exists

        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.zenapi = Zenoss(self.url, self.username, self.password, ssl_verify=False)

        if self.ip is not None:
            self.set_state_from_source()

        super(ZenConfig, self).__init__()

    def set_logger(self, logger):
        self.logger = logger

    def make_unicode_a_string(self, s):
        if isinstance(s, unicode):
            return str(s)
        else:
            return s

    def __eq__(self, other):

        if self.exists != other.exists:
            self.debug_log("exists status do not match for %s" % self.ip)
            return False
        if self.url != other.url:
            self.debug_log("endpoint urls do not match for %s" % self.ip)
            return False
        if self.name != other.name:
            self.debug_log("names do not match for %s" % self.ip)
            return False
        if other.priority is not None and self.priority != other.priority:
            self.debug_log("device priorities do not match for %s" % self.ip)
            return False
        #if other.productionstate is not None and self.productionstate != other.productionstate:
        #    self.debug_log("device groups do not match for %s" % self.ip)
        #    return False
        if not self.deviceclass.startswith(other.deviceclass):
            self.debug_log("device class parents do not match for %s" % self.ip)
            return False
        if not self.location.startswith(other.location):
            self.debug_log("device locations do not match for %s" % self.ip)
            return False

        if self.groups is None and other.groups is None:
            pass
        else:
            if None in (self.groups, other.groups):
                self.debug_log("device groups do not match for %s" % self.ip)
                return False
            else:
                a = list(set(self.groups)-set(other.groups))
                b = list(set(other.groups)-set(self.groups))
                c = len(a)+len(b)
                if c > 0:
                    # some difference exists
                    self.debug_log("device groups do not match for %s" % self.ip)
                    return False

        if self.systems is None and other.systems is None:
            pass
        else:
            if None in (self.systems, other.systems):
                self.debug_log("systems groups do not match for %s" % self.ip)
                return False
            else:
                a = list(set(self.systems)-set(other.systems))
                b = list(set(other.systems)-set(self.systems))
                c = len(a)+len(b)
                if c > 0:
                    # some difference exists
                    self.debug_log("systems groups do not match for %s" % self.ip)
                    return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)


    def verify_connectivity(self):
        tries = 0
        try_counter = 10
        while tries < try_counter:
            try:
                result = self.zenapi.get_device_classes('/Devices')
                if isinstance(result, list) and len(result) > 0:
                    classes = result
                    for dclass in classes:
                        if 'uid' in dclass and dclass['uid'] == '/zport/dmd/Devices/Discovered':
                            return True
            except Exception as e:
                pass

            sleep(10)
            tries += 1


        raise AssertionError("Unable to verify Zenoss API Health.")

    def set_state_from_source(self):
        """
        Intended to be called by the initiator when ip is passed to the constructor.
        """
        device = None
        try_again = False
        try:
            device = self.zenapi.find_device_by_ip(self.ip)
        except Exception as e:
            try_again = True

        if try_again:
            sleep(self.sleep_timer)
            try:
                device = self.zenapi.find_device_by_ip(self.ip)
            except Exception as e:
                pass

        if device is not None and isinstance(device, dict):
            self.exists = True
            self.priority = device.get('priority', None)
            self.productionstate = device.get('productionState', None)
            self.groups = self.filter_groups_to_managed(device.get('groups', None))
            self.systems = self.filter_systems_to_managed(device.get('systems', None))
            self.location = self.make_unicode_a_string(self.filter_location_to_name_only(device.get('location', None)))
            self.name = self.make_unicode_a_string(device.get('name', None))

            device_detailed = None
            tries = 10
            tried = 0
            while tried < tries:
                try:
                    device_detailed = self.zenapi.get_device_detailed(device.get('uid', None))['data']
                except Exception as e:
                    pass
                if device_detailed is not None:
                    break
                else:
                    sleep(self.sleep_timer)
                tried += 1

            if device_detailed is None:
                raise AssertionError("Something went wrong when try to get additional info for %s" % self.ip)

            if 'deviceClass' in device_detailed and 'uid' in device_detailed['deviceClass']:
                dclass_uid = device_detailed['deviceClass']['uid']
                prefix = '/zport/dmd/Devices'
                if dclass_uid.startswith(prefix):
                    self.deviceclass = self.make_unicode_a_string(dclass_uid[len(prefix):])
                else:
                    self.deviceclass = self.make_unicode_a_string(dclass_uid)
        else:
            self.exists = False

    def set_state_from_config_object(self, other):
        # return True, things works
        if self.exists and not other.exists:
            return self.remove_device()
        elif not self.exists and other.exists:
            #if the device does not exist, try to add it first.
            if self.add_device(other):
                pass
            else:
                raise AssertionError("Failed when trying to add %s" % self.ip)

        if other.exists:
            tries = 0
            while self != other and tries < self.tries:
                if self.name != other.name:
                    self.set_name(other.name)
                    sleep(self.sleep_timer)
                if other.priority is not None:
                    self.set_priority(other.priority)
                    sleep(self.sleep_timer)
                elif other.priority is None and self.priority is None:
                    self.set_priority(30)
                    sleep(self.sleep_timer)
                if other.productionstate is not None and not (self.exists and self.ignore_prodstate_if_exists):
                    self.set_productionstate(other.productionstate)
                    sleep(self.sleep_timer)
                elif other.productionstate is None and self.productionstate is None:
                    # default to pre-production
                    self.set_productionstate(500)
                    sleep(self.sleep_timer)
                self.set_groups(other.groups)
                self.set_systems(other.systems)
                if self.deviceclass is None or not self.deviceclass.startswith(other.deviceclass):
                    self.set_deviceclass(other.deviceclass)
                    sleep(self.sleep_timer)
                if self.location is None or not self.location.startswith(other.location):
                    self.set_location(other.location)
                    sleep(self.sleep_timer)
                if self != other:
                    sleep(self.sleep_timer)
                    tries += 1
            return self == other
        else:
            return False

    def filter_groups_to_managed(self, groups):
        managed_groups = []
        if groups is not None:
            for group_details in groups:
                if 'name' in group_details and group_details['name'].startswith('/Managed/') and group_details['name'] != '/Managed':
                    managed_groups.append('/'.join(group_details['name'].split('/')[2:]))
            return managed_groups
        else:
            return None

    def filter_systems_to_managed(self, systems):
        managed_systems = []
        if systems is not None:
            for system_details in systems:
                if 'name' in system_details and system_details['name'].startswith('/Managed/') and system_details['name'] != '/Managed':
                    managed_systems.append('/'.join(system_details['name'].split('/')[2:]))
            return managed_systems
        else:
            return None

    def filter_location_to_name_only(self, locationDict):
        if isinstance(locationDict, dict) and 'name' in locationDict:
            return locationDict['name'].strip('/')
        else:
            return ''

    def change_state(self, zenconfig_new):
        """
        :param zenconfig_new: A ZenConfig object that does not have an ip set and
        is the target configuration.
        :return: True, state set successfully.
        raise an Assertion error on failure
        """
        pass

    def add_device(self, other):
        result = self.zenapi.add_device(
                device_name=other.name,
                device_class=other.deviceclass,
                ip=self.ip,
                productionState=other.productionstate,
                priority=other.priority,
                locationPath=other.location,
            )

        if 'msg' in result and 'already exists' in result['msg'] and '/interfaces/' not in result['msg']:
        # ip address changed, let's deal with that
            self.zenapi.reset_ip(device_name=other.name, ip_address=self.ip)

        tries = 3
        try_counter = 0
        while not self.exists and try_counter < tries:
            sleep(3)
            try_counter += 1
            # self.set_state_from_source()
            self.set_state_from_source()

        return self.exists

    def remove_device(self):
        self.zenapi.remove_device(self.ip)
        sleep(60)
        try_counter = 0
        while self.exists and try_counter < self.tries:
            try_counter += 1
            sleep(self.sleep_timer)
            self.set_state_from_source()
        return not self.exists

    def set_name(self, newname):
        if self.name != newname:
            self.zenapi.rename_device(ip=self.ip, new_name=newname)
            try_counter = 0
            while self.name != newname and try_counter < self.tries:
                sleep(self.sleep_timer)
                try_counter += 1
                self.set_state_from_source()
            if self.name == newname:
                return True
            else:
                return False
        else:
            return True

    def set_priority(self, new_priority):
        if self.priority != new_priority:
            self.zenapi.set_priority(self.ip, new_priority)
            try_counter = 0
            while self.priority != new_priority and try_counter < self.tries:
                sleep(self.sleep_timer)
                try_counter += 1
                self.set_state_from_source()
            if self.priority == new_priority:
                return True
            else:
                return False
        else:
            return True

    def set_productionstate(self, new_prodstate):
        if new_prodstate is None:
            new_prodstate = 500
        if self.productionstate != new_prodstate:
            self.zenapi.set_prod_state(self.ip, new_prodstate)
            try_counter = 0
            while self.productionstate != new_prodstate and try_counter < self.tries:
                sleep(self.sleep_timer)
                try_counter += 1
                self.set_state_from_source()
            if self.productionstate == new_prodstate:
                return True
            else:
                return False
        else:
            return True

    def set_groups(self, new_groups):
        existing_groups = self.zenapi.get_groups()
        managed_exists = False
        groups = list()
        if 'groups' in existing_groups:
            for g in existing_groups['groups']:
                if g['name'].startswith('/Managed'):
                    managed_exists = True
                groups.append(g['name'])

        if not managed_exists:
            self.zenapi.add_group("/Managed")

        if self.groups is not None:
            missing_groups = list(set(new_groups)-set(self.groups))
            not_needed_groups = list(set(self.groups) - set(new_groups))
        else:
            missing_groups = new_groups
            not_needed_groups = []

        for group in [x for x in missing_groups if len(x) > 0]:
            group_path = '/Managed'
            for part in group.split('/'):
                self.zenapi.add_group(group_path + '/' + part)
                group_path += '/' + part
            self.zenapi.move_device(self.ip, "/zport/dmd/Groups/Managed/" + group)

        for group in not_needed_groups:
            self.zenapi.remove_device_from_managed_group_by_ip(self.ip, group)

        self.set_state_from_source()
        missing_groups = list(set(new_groups) - set(self.groups))
        not_needed_groups = list(set(self.groups) - set(new_groups))
        if not missing_groups and not not_needed_groups:
            return True
        else:
            return False

    def set_systems(self, new_systems):
        existing_systems = self.zenapi.get_systems()
        managed_exists = False
        systems = list()
        if 'systems' in existing_systems:
            for s in existing_systems['systems']:
                if s['name'].startswith('/Managed'):
                    managed_exists = True
                systems.append(s['name'])

        if not managed_exists:
            self.zenapi.add_systems("/Managed")

        if self.systems is not None:
            missing_systems = list(set(new_systems)-set(self.systems))
            not_needed_systems = list(set(self.systems) - set(new_systems))
        else:
            missing_systems = new_systems
            not_needed_systems = []

        for system in [x for x in missing_systems if len(x) > 0]:
            system_path = '/Managed'
            for part in system.split('/'):
                self.zenapi.add_systems(system_path + '/' + part)
                system_path += '/' + part
            self.zenapi.move_device(self.ip, "/zport/dmd/Systems/Managed/" + system)

        for system in not_needed_systems:
            self.zenapi.remove_device_from_managed_system_by_ip(self.ip, system)

        self.set_state_from_source()
        missing_systems = list(set(new_systems) - set(self.systems))
        not_needed_systems = list(set(self.systems) - set(new_systems))
        if not missing_systems and not not_needed_systems:
            return True
        else:
            return False

    def set_deviceclass(self, new_deviceclass):
        if not self.deviceclass.startswith(new_deviceclass):
            self.zenapi.move_device(self.ip, '/zport/dmd/Devices' + new_deviceclass)
            try_counter = 0
            while self.deviceclass != new_deviceclass and try_counter < self.tries:
                sleep(self.sleep_timer)
                try_counter += 1
                self.set_state_from_source()
            if self.deviceclass == new_deviceclass:
                return True
            else:
                return False
        else:
            return True

    def set_location(self, new_location):

        if new_location == '/':
            # don't allow movement to the top
            return False

        new_location = '/' + new_location.strip('/')
        if self.location != new_location:
            locations_raw = self.zenapi.get_locations()
            existing_locations = []
            if isinstance(locations_raw, dict) and 'locations' in locations_raw:
                for l in locations_raw['locations']:
                    existing_locations.append('/' + l['name'].strip('/'))

            new_location_parts = new_location.split('/')[1:]
            new_location_parts_path = ''
            for l in new_location_parts:
                if l not in existing_locations:
                    self.zenapi.add_location(new_location_parts_path, l)
                    new_location_parts_path += '/' + l
            print self.zenapi.move_device(self.ip, '/zport/dmd/Locations' + new_location)

            # verify
            try_counter = 0
            while self.location != new_location and try_counter < self.tries:
                sleep(self.sleep_timer)
                try_counter += 1
                self.set_state_from_source()
            if self.location != new_location:
                return False
            else:
                return True
        else:
            return True
