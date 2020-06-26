from idractemplate import IdracTemplate


class CitIdrac9Template(IdracTemplate):

    def __init__(self, username, password, url, record=None, priority=30, productionstate=None,
                 additional_groups='', additional_systems='', location_override=None):
        super(CitIdrac9Template, self).__init__(record, username, password, url, priority,
                                                     productionstate, additional_groups, additional_systems,
                                                     location_override)

        self.config['deviceclass'] = '/Server/Dell/iDRAC9/CIT'








