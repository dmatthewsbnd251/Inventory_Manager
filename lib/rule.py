"""Rule Class:
pass priority, criteria objects,
and/or other rulesto define a rule"""
import os
import inspect
import importlib
from lib.statetemplates.statetemplate import StateTemplate
from lib.criteria import Criteria


class Rule:

    rule_name = None
    priority = None
    rules = None
    criteria = None
    state_template_map = {}
    state_template = None
    state_template_kwargs = None
    config_name = None

    def __init__(self, rule_name, priority, state_template=None, kwargs=None,
                 config_name=None):

        if not isinstance(rule_name, basestring):
            raise ValueError("rule_name must be a string.")

        if not isinstance(priority, int):
            raise ValueError("priority must be an integer")

        # if passing kwargs the template must be set
        # if kwargs and not isinstance(state_template, basestring):
        #    raise ValueError("State template args were passed to the rule but the name of a template was not set.")

        if None in (state_template, kwargs, config_name) and (state_template is not None or kwargs is not None or
                                                              config_name is not None):
            raise ValueError("If state_template, kwargs, or config name is set, then all of the aforementioned "
                             "need set.")

        self.rule_name = str(rule_name)
        self.initialize_template_class_map()
        self.priority = priority
        self.rules = set()
        self.criteria = set()
        self.config_name = config_name
        if state_template is not None:
            if str(state_template) not in self.state_template_map:
                raise AssertionError("State template %s not found" % state_template)
            else:
                self.state_template = str(state_template)
        if kwargs is not None:
            self.state_template_kwargs = kwargs

    def __str__(self):

        outputStr = "\n"
        outputStr += "\trule name: %s\n" % self.rule_name
        outputStr += "\trule priority: %d\n" % self.priority
        if self.state_template is not None:
            outputStr += "\tstate template: %s\n" % self.state_template
        outputStr += "\trule criteria: \n"
        for cr in self.get_criteria():
            outputStr += str(cr)
        return outputStr

    def get_criteria(self):
        """Returns a set of criteria, descending into other rules
        objects or criteria objects as necessary."""

        all_criteria = set()
        for r in self.get_all_rules():
            all_criteria = all_criteria | r.criteria

        return all_criteria

    def get_all_rules(self, already_seen_rules=None):
        """Get rules and nested rules"""
        if already_seen_rules is None:
            already_seen_rules = set()
            already_seen_rules.add(self)

        for r in self.rules:
            if r not in already_seen_rules:
                already_seen_rules.add(r)
                already_seen_rules = r.get_all_rules(already_seen_rules)
        return already_seen_rules

    def add_criteria(self, c):
        if isinstance(c, Criteria):
            self.criteria.add(c)
        else:
            raise ValueError("Attempted to add criteria to a rule that was not a Criteria instance.")

    def add_rule(self, r):
        if isinstance(r, Rule):
            self.rules.add(r)
        else:
            raise ValueError("Attempted to add a rule to a rule instance that was not a Rule instance.")

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
