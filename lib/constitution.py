"""This class contains all of the rules,
criteria, and actions."""

from lib.criteria import Criteria
from lib.rule import Rule

class Constitution:

    criteria = set()
    rules = set()

    # state_template_options[config_name] = {
    #     options: value,
    #     options2: value2,
    #     ...
    # }
    state_template_options = {}
    required_datasources = []

    def __init__(self):
        pass

    def __str__(self):
        return_str = "Rules:\n"
        for r in self.get_next_rule_by_priority():
            return_str += str(r)
        return return_str

    def add_criteria(self, c):
        if not isinstance(c, Criteria):
            raise ValueError("Only criteria instances can be added to the critieria of the constitution.")
        else:
            self.criteria.add(c)

    def add_rule(self, r):
        if not isinstance(r, Rule):
            raise ValueError("Only rule instances can be added to the rules of the constitution.")
        else:
            self.rules.add(r)

    def load_legislation(self, config):

        #Load required data sources
        dsources = config.get("Monitoring", "required_datasources")
        for d in dsources.split(','):
            d = d.strip().lower()
            if d:
                self.required_datasources.append(d)
        """Input: ConfigParser object"""
        for section in config.sections():
            if section.startswith('Criteria ') and len(section) > 9:
                criteria_name = ''.join(section[9:]).lower()
                if 'reverse' in config.options(section):
                    reverse = config.getboolean(section, 'reverse')
                else:
                    reverse = False
                c = Criteria(criteria_name=criteria_name, reverse=reverse)
                hascriteria = False
                for key, val in config.items(section):
                    if key.startswith('criteria_name_'):
                        index = key[14:]
                        c.add_criteria(val, config.get(section, 'criteria_criteria_' + index))
                        hascriteria = True
                if hascriteria:
                    self.criteria.add(c)

            elif section.startswith("Config ") and len(section) > 7:
                config_name = ''.join(section[7:]).lower()
                self.state_template_options[config_name] = {}
                for key, val in config.items(section):
                    self.state_template_options[config_name][key] = val

        for section in config.sections():
            if section.startswith('Rule ') and len(section) > 5:
                rule_name = ''.join(section[5:]).lower()
                priority = config.getint(section, 'priority')
                criteria = set()
                if 'state_template' in config.options(section):
                    state_template = config.get(section, 'state_template')
                else:
                    state_template = None

                kwargs = None
                cfg = None
                if 'options_config' in config.options(section):
                    cfg = config.get(section, 'options_config').lower().strip()
                    kwargs = self.state_template_options[cfg]

                new_rule = Rule(rule_name=rule_name, priority=priority, state_template=state_template, kwargs=kwargs,
                                config_name=cfg)
                self.add_rule(new_rule)

                for key, val in config.items(section):
                    if key.startswith('rule_type_') and val.lower() == 'criteria':
                        index = ''.join(key[10:]).lower()
                        criteria.add(
                            self.find_criteria_by_name(
                                config.get(section, 'rule_name_' + index).lower()
                            )
                        )
                for c in criteria:
                    new_rule.add_criteria(c)

        for section in config.sections():
            if section.startswith('Rule ') and len(section) > 5:
                rule_target_name = ''.join(section[5:]).lower()
                for key, val in config.items(section):
                    if key.startswith('rule_type_') and val.lower() == 'rule':
                        index = ''.join(key[10:]).lower()
                        rule_source_name = config.get(section, 'rule_name_' + index).lower()
                        r_source = self.find_rule_by_name(rule_source_name)
                        r_target = self.find_rule_by_name(rule_target_name)
                        r_target.add_rule(r_source)

    def get_next_rule_by_priority(self):
        rules_priorities = {}
        for r in self.rules:
            rules_priorities[int(r.priority)] = r
        for p in sorted(rules_priorities.keys(), reverse=True):
            yield rules_priorities[p]

    def get_rules_with_templates_by_priority(self):
        for r in self.get_next_rule_by_priority():
            if r.state_template is not None:
                yield r

    def find_rule_by_name(self, name):
        for r in self.rules:
            if r.rule_name == name:
                return r
        return None

    def find_criteria_by_name(self, name):
        for c in self.criteria:
            if c.criteria_name == name:
                return c
        return None

