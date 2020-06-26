from citinfrastructurelinuxservertemplate import CitInfrastructureLinuxServerTemplate


class MysqlCitInfrastructureLinuxServerTemplate(CitInfrastructureLinuxServerTemplate):

    def __init__(self, username, password, url, record=None, priority=30, productionstate=None,
                 additional_groups='', additional_systems='', location_override=None):
        super(MysqlCitInfrastructureLinuxServerTemplate, self).__init__(record, username, password, url, priority,
                                                     productionstate, additional_groups, additional_systems,
                                                     location_override)

        self.config['deviceclass'] = '/Server/SSH/Linux/CIT/Infrastructure/MySQL'