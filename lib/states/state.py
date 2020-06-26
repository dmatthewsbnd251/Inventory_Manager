"""State: Abstract class that
defines the desired state of inventory in a target system"""

class State(object):

    def __init__(self):
        self.logger = None
        self.verify_connectivity()

    def verify_connectivity(self):
        raise NotImplementedError

    def set_logger(self):
        raise NotImplementedError

    def debug_log(self, log_string):
        """Pass positional logger arguments to a logger.debug method
        if a logger instance was instantiated"""
        if self.logger is not None:
            self.logger.debug(log_string)

    def info_log(self, log_string):
        """Pass positional logger arguments to a loger.info method
        if a logger instance was instantiated"""
        if self.logger is not None:
            self.logger.info(log_string)

    def __eq__(self, other):
        raise NotImplementedError("Method not properly implemented")

    def __ne__(self, other):
        raise NotImplementedError("Method not properly implemented")

    def set_state_from_source(self):
        """Set this state of this instance based on the actual
        configuration of the target."""
        raise NotImplementedError("Method not properly implemented")

    def set_state_from_config_object(other):
        """Set the state of this instance and the actual configuration
        at a target based on a another config object as a model."""
        raise NotImplementedError("Method not properly implemented")