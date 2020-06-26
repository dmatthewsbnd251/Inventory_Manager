"""DataSource is an abstract that all data sources
should implement"""

from lib.record import Record


class DataSource(object):

    connection_options = None
    entries = None
    inventory = None

    def __init__(self, connection_options=dict(), inventory=None):

        if not isinstance(connection_options, dict):
            raise ValueError("Connections options must be a dictionary.")
        self.connection_options = connection_options
        self.entries = list()
        self.inventory = inventory

    def scrape_data(self):
        """return: list of Record objects"""
        raise NotImplementedError

    def add_entry(self, entry):
        if not isinstance(entry, Record):
            raise ValueError("Entries must be record objects.")
        self.entries.append(entry)
