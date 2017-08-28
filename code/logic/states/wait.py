from logic.statemachine import *

class WaitState(State):
    """ Abstract superclass for all state machine states """

    def on_enter(self):
        """ Called when this state is entered"""
        pass

    def on_exit(self):
        """ Called when this state is exited"""
        pass

    @property
    def pipeline(self):
        raise NotImplementedError()

    def on_update(self, hist):
        """ Called on every update."""
        raise NotImplementedError()
