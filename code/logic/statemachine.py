from sensors import pipeline
from utils.functions import overrides
from motor import movement


class StateMachine(object):
    """ The interface to the state machine. """

    def __init__(self):
        self.__current_state = _InitialState()

        self.__history = []

    def run(self):
        while True:
            self.update()

    def update(self):
        pipeline_out = self.__current_state.pipeline.run_pipeline(None)
        self.__history.append(pipeline_out)
        next_state = self.__current_state.on_update(self.__history)
        self.set_state(next_state)

    def set_state(self, state: State):
        if state is not self.__current_state:
            self.__current_state.on_exit()
            self.__current_state = state
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

