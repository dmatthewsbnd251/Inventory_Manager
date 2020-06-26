
class StateTemplate(object):

    def __init__(self, record):
        self.config = {}
        self.record = record

    def get_state_object(self):
        raise AssertionError("Method not implemented.")

    def __str__(self):
        return self.__class__.__name__

    def get_current_state_object(self):
        raise AssertionError("Method not implemented.")