from sensors import pipeline
from utils.functions import overrides, current_time_millis
import logging


class StateMachine(object):
    """ The interface to the state machine. """

    def __init__(self):
        self._current_state = _InitialState()

        self.__history = []

    def run(self):
        try:
            while True:
                self.update()
        except KeyboardInterrupt:
            self._current_state.on_exit()

    def update(self):
        logging.debug("\nUpdating state machine (current state: " + str(self._current_state) + ")")
        start = current_time_millis()
        pipeline_out = self._current_state.pipeline.run_pipeline(None)
        self.__history.append(pipeline_out)
        next_state = self._current_state.on_update(self.__history)
        self.set_state(next_state)
        logging.debug("State machine updated ({}ms). New state: {}".format(
            current_time_millis() - start, self._current_state))

    def set_state(self, state):
        if state is not self._current_state:
            self._current_state.on_exit()
            self._current_state = state
            print("current state", state)
            state.on_enter()


class State(object):
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

    def __str__(self):
        return self.__class__.__name__


class _InitialState(State):

    def __init__(self):
        State.__init__(self)
        self.first_state = self

    def on_enter(self):
        pass

    def on_exit(self):
        pass

    @property
    def pipeline(self):
        return pipeline.EmptyPipeline()

    @overrides(State)
    def on_update(self, hist):
        return self.first_state

