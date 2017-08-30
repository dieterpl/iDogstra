

from logic.states import *


class IDog(StateMachine):

    def __init__(self):
        StateMachine.__init__(self)

        logging.debug("Starting BT-Dongles")
        config.BT_DONGLES = [bluetooth.BTDongle(i, config.BT_TARGET_UUID) for i in range(2)]
        for dongle in config.BT_DONGLES:
            dongle.start()

        self._current_state.first_state = SearchState()





