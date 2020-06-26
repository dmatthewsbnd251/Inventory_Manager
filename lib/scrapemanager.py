from lib.inventory import Inventory

class ScrapeManager:

    def __init__(self):

        self.datasources = dict()

    def add_datasource(self, datasource_class, connection_options, section, depends):

        if not isinstance(datasource_class, basestring):
            raise ValueError("datasource_class must be a string.")

        datasource_class = str(datasource_class)

        if not isinstance(connection_options, dict):
            raise ValueError("connection_options must be a dictionary.")

        if not isinstance(section, basestring):
            raise ValueError("section must be a string")

        section = str(section)

        if not isinstance(depends, list):
            raise ValueError("depends must be a list")

        # clean up the entry name to something less ugly
        if section.startswith('DataSource '):
            section = ''.join(section.split('DataSource ')[1:])
        section_name_clean = section.replace(" ", "_").lower()

        self.datasources[section_name_clean] = {
            'datasource_class': datasource_class,
            'connection_options': connection_options,
            'depends': depends
        }

    def validate_datasource_integrity(self):

        datasource_names = self.datasources.keys()

        for d in self.datasources:
            for dep in self.datasources[d]['depends']:
                if dep not in datasource_names:
                    raise AssertionError("A dependency was listed that was not added as a data source.")

    def get_inventory(self):

        inventory = Inventory()
        inventory_to_process = set(self.datasources.keys())
        processed_datasources = set()
        maxloops = 1000
        loops = 0

        while inventory_to_process - processed_datasources and loops < maxloops:

            for ds in self.datasources:
                if ds not in processed_datasources:
                    deps_met = True
                    for dep in self.datasources[ds]['depends']:
                        if dep not in processed_datasources:
                            deps_met = False

                    if deps_met:
                        dep_class = self.datasources[ds]['datasource_class']
                        connection_options = self.datasources[ds]['connection_options']
                        datasource_name = ds

                        inventory.import_data_source(datasource_class=dep_class, connection_options=connection_options,
                                                     datasource_name=datasource_name, inventory=inventory)

                        processed_datasources.add(ds)
            loops += 1

        if inventory_to_process - processed_datasources:
            raise AssertionError("Not all data sources were processed.  Make sure there isn't a dependency loop.")

        return inventory



