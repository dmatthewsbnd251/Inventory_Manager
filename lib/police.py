"""Police Class
Pass a record object and the constitution to init.  The Police
object enforces the rules on a record"""

from lib.constitution import Constitution
from lib.statetemplates.statetemplate import StateTemplate
from lib.inventory import Inventory
import os
import inspect
import importlib
from logging import Logger
from collections import Iterable
import re
import sys
import csv

class Police:

    constitution = None
    inventory = None
    logger = None
    state_template_map = {}

    def __init__(self, constitution, inventory, logger):
        if not isinstance(constitution, Constitution):
            raise ValueError("Constitution must be a Constitution instance.")

        if not isinstance(inventory, Inventory):
            raise ValueError("inventory must be an Inventory instance")

        if not isinstance(logger, Logger):
            raise ValueError("logger must be a Logger instance.")

        self.constitution = constitution
        self.inventory = inventory
        self.logger = logger
        self.initialize_template_class_map()

        if self.are_datasources_missing():
            raise AssertionError("Not all required datasources were found in the source json file.")

    def are_datasources_missing(self):

        ds_missing = list(set(self.constitution.required_datasources) - set(self.inventory.datasources))
        if len(ds_missing) > 0:
            self.logger.debug("Missing datasources: %s" % ds_missing)
            return True
        else:
            return False

    def screen_attribute(self, pattern, attribute):
        if isinstance(attribute, Iterable) and not isinstance(attribute, basestring):
            for a in attribute:
                if self.screen_attribute(pattern, a):
                    return True
            return False
        else:
            try:
                attribute = str(attribute)
            except Exception:
                attribute = ''
            matchobj = re.match(pattern, attribute, flags=re.I)
            if matchobj:
                return True
            else:
                self.logger.debug("%s did not match %s" % (pattern, attribute))
                return False

    def screen_record(self, record, rule):
        """Bool: True = meets rule criteria"""
        all_criteria = rule.get_criteria()
        record_attribs = record.get_attribute_dict()
        for crit_instance in all_criteria:
            for crit_name, crit_pattern in crit_instance.get_next_criteria():
                if crit_name in record_attribs:
                    self.logger.debug("Testing %s value %s against %s for pattern %s" % (
                    record.ip, record_attribs[crit_name], crit_name, crit_pattern))
                    result = self.screen_attribute(crit_pattern, record_attribs[crit_name])
                    if result and crit_instance.reverse:
                        return False
                    elif not result and not crit_instance.reverse:
                        return False
                elif not crit_instance.reverse:
                    self.logger.debug("Not testing %s against criteria '%s' for pattern %s because this record does" \
                                      "not have that attribute." % (record.ip, crit_name, crit_pattern,))
                    return False
        return True

    def dry_run(self):
        self.run_tests_and_apply_if_allowed(applythis=False)

    def stats_only(self, additional_fields=None):
        if additional_fields is not None:
            if not isinstance(additional_fields, list):
                raise ValueError("Additional fields must be a list or None")
        return self.run_tests_and_apply_if_allowed(applythis=False, stats_only=True,
                                                   extra_fields=additional_fields)

    def print_stats_as_csv(self, additional_fields=None):
        stats_dict = self.stats_only(additional_fields)
        header_row = ['ip', 'template_name', 'rule_name', 'config_name']

        for a in additional_fields:
            header_row.append(a)

        csv_output = csv.DictWriter(sys.stdout, fieldnames=header_row)
        csv_output.writeheader()
        rows = list()
        for ip in stats_dict:
            row_dict = {
                'ip':ip
            }
            row_dict.update(stats_dict[ip])
            rows.append(row_dict)
        csv_output.writerows(rows)

    def run_tests_and_apply_if_allowed(self, applythis=False, stats_only=False, extra_fields=None):
        """Runs the tests, if apply is True, will apply them.  Extra fields must be a list of additional
        attributes to include in the stats csv output.
        Return: stats about the state based on the configuration"""

        stats = {}
        # stats = {
        #    record = {
        #              'template': StateTemplate,
        #              'config': ConfigTemplate
        #             }
        # }

        for record in self.inventory.get_inventory():
            self.logger.debug("Begin processing %s" % record.ip)
            rule_passed = None
            for rule in self.constitution.get_rules_with_templates_by_priority():
                if rule.priority > -1:
                    self.logger.debug("Checking %s against rule %s" % (record.ip, rule.rule_name))
                    if self.screen_record(record, rule):
                        rule_passed = rule
                        break

            if rule_passed is None:
                self.logger.debug("%s did not pass any rule criteria" % record.ip)

            else:
                if not stats_only:
                    self.logger.debug("%s passed criteria, ensuring the state %s is met." % (record.ip, rule.state_template))
                    if rule.state_template is not None:

                        template_class = self.state_template_map[rule.state_template]
                        template_instance = template_class(record=record, **rule.state_template_kwargs)
                        cur_state = template_instance.get_current_state_object()
                        desired_state = template_instance.get_state_object()

                        #Enable logging of the states if method is implemented
                        try:
                            cur_state.set_logger(self.logger)
                        except NotImplementedError:
                            self.logger.debug("Logging not implemented on cur_state template object %s" % record.ip)

                        try:
                            desired_state.set_logger(self.logger)
                        except NotImplementedError:
                            self.logger.debug("Logging not implemented on desired_state template object %s" % record.ip)

                        if cur_state != desired_state:
                            self.logger.info("%s is not at the desired state." % record.ip)
                            if applythis:
                                self.logger.info("Applying state to %s" % record.ip)
                                try:
                                    if cur_state.set_state_from_config_object(desired_state):
                                        self.logger.info("State applied successfully to %s." % record.ip)
                                except AssertionError as e:
                                    self.logger.info(e)
                                    self.logger.info("Skipping..")
                                    pass
                            else:
                                self.logger.info("Not setting state for %s.  Dry-run detected." % record.ip)
                        else:
                            self.logger.debug("%s is already at the desired state." % record.ip)

                    else:
                        self.logger.debug("Rule %s does not have a template co"
                                          "nfigured.  Applying nothing to %s" %
                                          (rule.rule_name, record.ip))
                else:

                    stats[record.ip] = {
                        'template_name': rule.state_template,
                        'rule_name': rule.rule_name,
                        'config_name': rule.config_name,
                    }
                    if extra_fields is not None:
                        attributes = record.get_attribute_dict()
                        for e in extra_fields:
                            if e in attributes:
                                stats[record.ip][e] = record.attributes[e]
                self.logger.debug("Finished processing %s" % record.ip)

        return stats

    def enforce(self):
        self.run_tests_and_apply_if_allowed(applythis=True)

    def initialize_template_class_map(self):
        ds_path = os.path.dirname((os.path.realpath(__file__))) + "/statetemplates"
        for root, dirs, files in os.walk(ds_path):
            for f in files:
                if f.endswith('.py') and f not in ('__init__.py', 'statetemplate.py'):
                    module_name = 'lib.statetemplates.' + ''.join(f.split('.')[:-1])
                    module_instance = importlib.import_module(module_name)
                    functions = inspect.getmembers(module_instance, inspect.isclass)

                    for name, member in functions:
                        if inspect.isclass(member) and issubclass(member, StateTemplate) and name != 'StateTemplate':
                            self.state_template_map[name] = member