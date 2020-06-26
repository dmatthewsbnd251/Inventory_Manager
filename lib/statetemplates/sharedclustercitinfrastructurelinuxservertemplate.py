from citinfrastructurelinuxservertemplate import CitInfrastructureLinuxServerTemplate


class SharedClusterCitLinuxInfrastructureLinuxServerTemplate(CitInfrastructureLinuxServerTemplate):

    def __init__(self, record=None, username=None, password=None, url=None, priority=30, productionstate=None,
                 additional_groups='', additional_systems='', location_override=None):
        super(SharedClusterCitLinuxInfrastructureLinuxServerTemplate, self).__init__(record, username, password, url, priority,
                                                     productionstate, additional_groups, additional_systems,
                                                     location_override)

        self.config['deviceclass'] = '/Server/SSH/Linux/CIT/Infrastructure/Shared Cluster'
