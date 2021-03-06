import argparse
import logging
import time
from sensors.bluetooth import bluetooth
from logic import camera_test_sm, iDog_sm, bt_test_sm
from config import *


known_state_machines = {
    "test-camera": camera_test_sm.CameraTestSM,
    "default": iDog_sm.IDog,
    "bt-test": bt_test_sm.BTTestSM
}


def main():
    """ Application entry point. """

    sm, smargs = __parse_args()
    __prepare_logs()

    if sm not in known_state_machines:
        logging.error("Unkown state machine '{}'".format(sm))
    else:
        logging.debug("Starting application with state machine {}".format(sm))
        sm_class = known_state_machines[sm]
        sm_class(*smargs).run()


def __parse_args():
    parser = argparse.ArgumentParser(description="iDogstra - the world's best dog AI since 1753")
    parser.add_argument("sm", type=str, help='What state machine to execute')
    parser.add_argument("smargs", nargs="*", help="Arguments to pass to the state machine")
    parser.add_argument('-v', '--verbose', action='store_const', const=True, default=False, help='Set verbose output')

    args = parser.parse_args()

    config.DEBUG_MODE = config.DEBUG_MODE or args.verbose
    return args.sm, args.smargs


def __prepare_logs():
    logfile = os.path.join(config.LOGSPATH, time.strftime('%Y%m%d %H-%M-%S'))
    if not os.path.exists(config.LOGSPATH):
        os.makedirs(config.LOGSPATH)

    logging.basicConfig(
        level=logging.DEBUG if config.DEBUG_MODE else logging.WARNING,
        format="%(asctime)10.10s [%(levelname)-5.5s] %(message)s",
        datefmt="%H:%M:%S",
        filename=logfile
    )
    logging.getLogger().addHandler(logging.StreamHandler())


if __name__ == "__main__":
    main()



