"""The criteria used by rule objects"""

class Criteria:

    criteria = None
    reverse = None
    criteria_name = None

    def __init__(self, criteria_name, reverse=False):
        """criteria = {
            record_attribute: regex,
            ..
            reverse reverses the result.
        }"""
        if not isinstance(criteria_name, basestring):
            raise ValueError("Criteria name must be a string.")

        if not isinstance(reverse, bool):
            raise ValueError("reverse must be a boolean value")

        self.criteria_name = str(criteria_name)
        self.criteria = {}
        self.reverse = reverse

    def get_next_criteria(self):
        """return Iterator:
        tuple(key, regex)"""
        for key in self.criteria:
            yield (key, self.criteria[key])

    def add_criteria(self, name, regex):
        if not isinstance(name, basestring) or not isinstance(regex, basestring):
            raise ValueError("arguments must be strings to criteria")
        self.criteria[str(name)] = str(regex)

    def __str__(self):
        outputStr = "\n"
        outputStr += "\t\tname: %s\n" % self.criteria_name
        outputStr += '\t\treverse: %s\n\t\tPatterns:\n' % str(self.reverse)
        for key in self.criteria:
            outputStr += "\t\t\t" + key + ": " + self.criteria[key] + "\n"
        return outputStr
