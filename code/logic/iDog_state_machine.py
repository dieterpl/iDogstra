
from logic.statemachine import *
from logic.states import *


class IDog(StateMachine):

    def __init__(self):
        StateMachine.__init__(self)
        self._current_state.first_state = SearchState()





