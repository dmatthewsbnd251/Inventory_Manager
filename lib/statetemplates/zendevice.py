from lib.statetemplates.statetemplate import StateTemplate
from lib.states.zenconfig import ZenConfig
import re


class ZenDevice(StateTemplate):

    """

    """
    def __init__(self, record=None, username=None, password=None, url=None,  priority=30, productionstate=None, additional_groups='',
                 additional_systems='', location_override=None, exists=True):
        super(ZenDevice, self).__init__(record)

        # Set exists to true
        if isinstance(exists, str) or isinstance(exists, unicode):
            if str(exists).lower().strip() == 'false':
                self.config['exists'] = False
            elif str(exists).lower().strip() == 'true':
                self.config['exists'] = True;
            else:
                raise ValueError("exists value is a string but is not set to True or False")

        elif isinstance(exists, bool):
            self.config['exists'] = exists

        # Setup API connection details
        self.config['username'] = username
        self.config['password'] = password
        self.config['url'] = url
        self.config['location'] = location_override

        # Configure the name parameter
        self.config['name'] = None
        if 'lookup_fqdn' in self.record.attributes:
            self.config['name'] = self.record.attributes['lookup_fqdn']
        elif 'sccm_fqdn' in self.record.attributes:
            self.config['name'] = self.record.attributes['sccm_fqdn']
        elif 'satellite_name' in self.record.attributes and self.is_fqdn(self.record.attributes['satellite_name']):
            self.config['name'] = self.record.attributes['satellite_name']
        elif 'v_name' in self.record.attributes and self.is_fqdn(self.record.attributes['v_name']):
            self.config['name'] = self.record.attributes['v_name']
        elif 'zenvsphere_guestname' in self.record.attributes and \
                self.is_fqdn(self.record.attributes['zenvsphere_guestname']):
            self.config['name'] = self.record.attributes['zenvsphere_guestname']

        # Clean-up the name formatting a little
        if self.config['name'] is not None:
            self.config['name'] = self.config['name'].lower().strip()

        # Set up groups
        groups = []
        if 'v_type' in self.record.attributes:
            groups.append('v/v_type/' + self.record.attributes['v_type'])

        if 'v_owner' in self.record.attributes:
            groups.append('v/v_owner/' + self.record.attributes['v_owner'])

        if 'v_os' in self.record.attributes:
            groups.append('v/v_os/' + self.record.attributes['v_os'])

        if 'v_class' in self.record.attributes:
            groups.append('v/v_class/' + self.record.attributes['v_class'])

        if 'v_payee' in self.record.attributes:
            groups.append('v/v_payee/' + self.record.attributes['v_payee'])

        if 'v_rack' in self.record.attributes and self.record.attributes['v_rack'] not in ('.','-0','na','0','-'):
            groups.append('v/rack/' + self.record.attributes['v_rack'])

        if 'v_status' in self.record.attributes:
            groups.append('v/status/' + self.record.attributes['v_status'])

        if 'satellite_location_name' in self.record.attributes:
            groups.append('satellite/location/' + self.record.attributes['satellite_location_name'])

        if 'satellite_hostgroup_name' in self.record.attributes:
            groups.append('satellite/hostgroup_name/' + self.record.attributes['satellite_hostgroup_name'])

        if 'satellite_environment_name' in self.record.attributes:
            groups.append('satellite/environment/' + self.record.attributes['satellite_environment_name'])

        if 'satellite_hostgroup_title' in self.record.attributes:
            groups.append('satellite/hostgroup_title/' + self.record.attributes['satellite_hostgroup_title'])

        if 'satellite_operatingsystem_name' in self.record.attributes:
            groups.append('satellite/os/' + self.record.attributes['satellite_operatingsystem_name'])

        if 'sccm_class' in self.record.attributes:
            groups.append('sccm/class/' + self.record.attributes['sccm_class'])

        if 'sccm_collection' in self.record.attributes and isinstance(self.record.attributes['sccm_collection'], list):
            for c in self.record.attributes['sccm_collection']:
                groups.append('sccm/collection/' + c)

        if 'zenvsphere_cluster' in self.record.attributes:
            groups.append('vmware/cluster/' + self.record.attributes['zenvsphere_cluster'])

        if 'zenvsphere_host' in self.record.attributes:
            groups.append('vmware/host/' + self.record.attributes['zenvsphere_host'])

        groups = list(set(groups + additional_groups.split(',')))
        self.config['groups'] = groups

        # Set up systems
        systems = []
        systems = list(set(systems + additional_systems.split(',')))
        self.config['systems'] = systems

        # Set up location
        if location_override is not None:
            self.config['location'] = location_override
        elif 'v_building' in self.record.attributes and 'v_room' in record.attributes:
            self.config['location'] = record.attributes['v_building'] + '/' + record.attributes['v_room']
        elif not self.config['location']:
            self.config['location'] = "Unknown"

        # Set up priority
        if priority is not None:
            self.config['priority'] = int(priority)
        else:
            self.config['priority'] = priority

        # Set up production state
        if productionstate is not None:
            self.config['productionstate'] = int(productionstate)
        else:
            self.config['productionstate'] = productionstate

    def get_current_state_object(self):
        return ZenConfig(ip=self.record.ip, username=self.config['username'], password=self.config['password'],
                         url=self.config['url'])

    def is_fqdn(self, hostname):
        if len(hostname) > 255:
            return False
        if hostname[-1] == ".":
            hostname = hostname[:-1]  # strip exactly one dot from the right, if present
        allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
        return all(allowed.match(x) for x in hostname.split("."))

    def get_state_object(self):

        return ZenConfig(
            username=self.config['username'],
            password=self.config['password'],
            url=self.config['url'],
            deviceclass='/Discovered',
            priority=self.config['priority'],
            productionstate=self.config['productionstate'],
            groups=self.config['groups'],
            systems=self.config['systems'],
            location=self.config['location'],
            name=self.config['name'],
            exists=self.config['exists'],
        )