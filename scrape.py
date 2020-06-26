#! /usr/bin/python

import sys, os
from ConfigParser import ConfigParser
import logging
from logging.config import fileConfig
from optparse import OptionParser
from lib.scrapemanager import ScrapeManager

# Always behave as though running from the location of this script
os.chdir(os.path.dirname(sys.argv[0]))

parser = OptionParser(usage="usage: %prog [options] filename",
                      version="%prog 1.0")

parser.add_option("-p", "--print-data",
                  action="store_true",
                  dest="print_data",
                  default=False,
                  help="Print the results of data gathering")

parser.add_option("-k", "--print-keys",
                  action="store_true",
                  dest="print_keys",
                  default=False,
                  help="Print the available keys with counts")

parser.add_option("-d", "--dry-run",
                  action="store_true",
                  dest="dry_run",
                  default=False,
                  help="Do not do anything.  Just determine what would be done and say why.")

parser.add_option("-j", "--json-file",
                  action="store",
                  dest="jfile",
                  default=None,
                  help="Optionally specify and output file for the data in json format.")

(options, args) = parser.parse_args()

fileConfig('logging.ini')
logger = logging.getLogger()

parser = ConfigParser()
config = 'inventory.ini'
parser.read(config)
scrapemanager = ScrapeManager()

logger.info("Parsing configuration for data sources.")
for section in parser.sections():
    if section.startswith('DataSource '):
        logger.info("Found a datasource configured.  Attempting to load %s" % section)
        connection_options = {}
        datasource_class = None
        depends = []
        for key, val in parser.items(section):
            if key == 'class':
                datasource_class = val
            elif key == 'depends':
                for d in val.split(','):
                    depends.append(d.lower().strip())
            else:
                connection_options[key] = val


        scrapemanager.add_datasource(
            datasource_class=datasource_class,
            connection_options=connection_options,
            section=section,
            depends=depends,
        )
'''
        #try:
            inventory.import_data_source(
                datasource_class=datasource_class,
                connection_options=connection_options,
                datasource_name=section,
            )'''

inventory = scrapemanager.get_inventory()


        #except Exception as e:
        #    logger.error("Failed to load %s.  Reason: %s" % (section, e), exc_info=True)
        #    # would be better to fail than process on a failed data source.
        #    sys.exit()

        #else:
        #    logger.info("Loaded %s" % section)

if options.print_data:
    print inventory

if options.print_keys:
    inventory.print_keys()

if parser.getint('Scrape', 'safety_limit') > inventory.get_attribute_count():
    logger.critical('Failed to gather enough data points. %d data points gathered.' % inventory.get_attribute_count())
    sys.exit(-1)

if options.jfile is not None:
    logger.info("json file specified.  Writing to %s" % options.jfile)
    with open(options.jfile, 'w') as f:
        f.write(inventory.get_json())
    f.close()

