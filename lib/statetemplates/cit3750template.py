from zendevice import ZenDevice
from lib.states.zenconfig import ZenConfig


class Cit3750Template(ZenDevice):
    """
    Set:
    exists
    name
    url
    username
    password
    priority
    productionstate
    groups
    systems
    deviceclass
    location
    Not Set:

    get_current_state_object implemented:
    True

    get_state_object implemented:
    True
    """

    def __init__(self, record=None, username=None, password=None, url=None, priority=30, productionstate=None,
                 additional_groups='', additional_systems='', location_override=None):
        super(Cit3750Template, self).__init__(record, username, password, url, priority, productionstate,
                                                  additional_groups, additional_systems, location_override)

        self.config['deviceclass'] = '/Network/Cisco/CIT/3750'

    def get_state_object(self):

        required_attribs = ['exists', 'name', 'url', 'username', 'password', 'priority',
                            'productionstate', 'groups', 'systems', 'deviceclass',
                            'location', 'exists', ]

        missing = set(required_attribs) - set(self.config.keys())
        if len(missing) > 0:
            raise ValueError("Not all required attributes were set before trying to generate "
                             "a state object.")

        return ZenConfig(
            username=self.config['username'],
            password=self.config['password'],
            url=self.config['url'],
            deviceclass=self.config['deviceclass'],
            priority=self.config['priority'],
            productionstate=self.config['productionstate'],
            groups=self.config['groups'],
            systems=self.config['systems'],
            location=self.config['location'],
            name=self.config['name'],
            exists=self.config['exists']
        )









