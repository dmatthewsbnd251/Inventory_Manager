#! /usr/bin/python

from ConfigParser import ConfigParser
import logging
from logging.config import fileConfig
from lib.inventory import Inventory
import os
import sys
from optparse import OptionParser
from lib.constitution import Constitution
from lib.police import Police


# Always behave as though running from the location of this script
os.chdir(os.path.dirname(sys.argv[0]))

fileConfig('logging.ini')
logger = logging.getLogger()

parser = OptionParser(usage="usage: %prog [options] filename",
                      version="%prog 1.0")
parser.add_option("-p", "--print-data",
                  action="store_true",
                  dest="print_data",
                  default=False,
                  help="Print the results of the data import and do nothing")

parser.add_option("-s", "--show-detail",
                  action="store_true",
                  dest="show_detail",
                  default=False,
                  help="Print the details of rules and criteria found.")

parser.add_option('-d', "--dry-run",
                  action="store_true",
                  dest="dry_run",
                  default=False,
                  help="Do not apply anything, just log what would have been done.")

parser.add_option('-c', "--csv",
                  action="store_true",
                  dest="csv",
                  default=False,
                  help="Do not apply anything, just run stats on what the final states should be"
                       " and return a csv.")

parser.add_option('-e', "--extra",
                  action="store",
                  dest="extra",
                  default=False,
                  help="Comma separated additional attributes to include in csv output. Ex: lookup_fqdn, "
                       "sccm_collection")

(options, args) = parser.parse_args()

config_parser = ConfigParser()
config = 'monitoring.ini'
config_parser.read(config)

json_file = config_parser.get('Monitoring', 'source_json')
logger.info("Loading json data from %s" % json_file)

if options.extra and not options.csv:
    logger.critical("CSV extra options passed but the CSV flag was not set.")
    sys.exit(-1)

inv = Inventory(json_file=json_file)
con = Constitution()
con.load_legislation(config_parser)
pol = Police(con, inv, logger)

if options.print_data:
    print inv

elif options.show_detail:
    print con

elif options.dry_run:
    pol.dry_run()

elif options.csv:
    additional_fields = []
    if options.extra:
        for o in options.extra.split(','):
            if len(o):
                additional_fields.append(o.lower())
    # from pprint import pprint
    # pprint(pol.stats_only(additional_fields))
    pol.print_stats_as_csv(additional_fields)

else:
    pol.enforce()

# if options.show_detail:
#    print constitution
