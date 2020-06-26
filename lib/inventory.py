"""The inventory class is the highest level object to the inventory
data structure."""
import json
from record import Record
import os
import importlib
import inspect
from lib.datasources.datasource import DataSource


class Inventory:

    # inventory stored as a dict with ip => record_object. They keys are the ip of each device.
    inventory = dict()
    datasource_class_map = dict()
    datasources = list()

    def __init__(self, json_file=None):

        # object name to type identifier
        self.initialize_datasource_class_map()

        if json_file is not None:
            with open(json_file) as json_data:
                raw_data = json.load(json_data)
                json_data.close()

            self.datasources = raw_data['data_sources']

            for ip in raw_data['inventory']:
                r = Record(ip)
                for attribute in raw_data['inventory'][ip]:
                    r.add_attribute(attribute_name=str(attribute),
                                    attribute_value=raw_data['inventory'][ip][attribute])
                    self.inventory[ip] = r

    def import_data_source(self, datasource_class, connection_options, datasource_name, inventory):
        """Adds a new data source to the inventory.  kwargs
        is used here to provide the credentials needed to
        access the data source. data_source_type passed should
        match the module name to use."""

        if not isinstance(inventory, Inventory):
            raise ValueError("inventory must be an inventory instance.")

        # find the datasource dynamically and also instantiate an instance with the
        # connection options.
        ds = self.datasource_class_map[datasource_class](connection_options, inventory)
        results = ds.scrape_data()
        self.merge_data(results, datasource_name)
        self.datasources.append(datasource_name)

    def merge_data(self, results, datasource_name):

        for entry in results:
            # prefix the rows with the datatype
            add_stack = dict()
            for row in entry.attributes:
                row_prefixed = datasource_name + "_" + row
                add_stack[row_prefixed] = entry.attributes[row]

            # Add an attribute to simply say this record is in the data source.
            add_stack[datasource_name + '_exists'] = True

            entry.attributes = add_stack

            if entry.ip in self.inventory:
                r = self.inventory[entry.ip]
                for key in entry.attributes:
                    r.add_attribute(key, entry.attributes[key])
                self.inventory[entry.ip] = r
            else:
                self.inventory[entry.ip] = entry

    def __str__(self):
        returnStr = ''
        for ip in self.inventory:
            returnStr += "Record: %s\n" % ip
            for a in self.inventory[ip].attributes:
                returnStr += "%s: %s\n" % (a, self.inventory[ip].attributes[a])
            returnStr += "\n"
        return returnStr

    def get_attribute_count(self):
        count = 0
        for record in self.inventory:
            count += len(self.inventory[record].attributes)
        return count

    def print_keys(self):
        keys = dict()
        for record in self.inventory:
            for attribute in self.inventory[record].attributes:
                if attribute in keys:
                    keys[attribute] += 1
                else:
                    keys[attribute] = 1
        for key, value in sorted(keys.iteritems(), key=lambda (k, v): (v, k)):
            print "%s\t%s" % (value, key)

    def get_json(self):
        output_dict = {
            'data_sources': self.datasources,
            'inventory': dict()
        }
        for ip in self.inventory:
            output_dict['inventory'][ip] = self.inventory[ip].get_attribute_dict()
        return json.dumps(output_dict)

    def initialize_datasource_class_map(self):
        ds_path = os.path.dirname((os.path.realpath(__file__))) + "/datasources"
        for root, dirs, files in os.walk(ds_path):
            for f in files:
                if f.endswith('.py') and f not in ('__init__.py', 'datasource.py'):
                    module_name = 'lib.datasources.' + ''.join(f.split('.')[:-1])
                    module_instance = importlib.import_module(module_name)
                    functions = inspect.getmembers(module_instance, inspect.isclass)

                    for name, member in functions:
                        if inspect.isclass(member) and issubclass(member, DataSource) and name != 'DataSource':
                            self.datasource_class_map[name] = member

    def get_inventory(self):
        for ip in self.inventory:
            yield self.inventory[ip]

    def get_ips(self):
        for ip in self.inventory.keys():
            yield ip


