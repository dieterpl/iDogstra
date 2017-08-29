import argparse
from config import *
import logging
import time
import logic.iDog_state_machine
import logic.find_threshold_sm
from sensors.bluetooth import bluetooth
from sensors.camera import camera


def main():
    """ Application entry point. """

    mode = __parse_args()
    __prepare_logs()
    logging.debug("Starting application in mode {}".format(mode))

    logging.debug("Starting BT-Dongles")
    config.BT_DONGLES = [bluetooth.BTDongle(i, config.BT_TARGET_UUID) for i in range(2)]
    for dongle in config.BT_DONGLES:
        dongle.start()

    if mode == "default":
        logic.iDog_state_machine.IDog().run()
    elif mode == "cameratest":
        camera.test()
    elif mode == "find-threshold":
        logic.find_threshold_sm.FindThresholdSM().run()
    else:
        logging.error("Unkown mode '{}'".format(mode))


def __parse_args():
    parser = argparse.ArgumentParser(description="iDogstra - the world's best dog AI since 1753")
    parser.add_argument('mode', type=str, help='What state machine to execute')
    parser.add_argument('-v', '--verbose', action='store_const', const=True, default=False, help='Set verbose output')

    args = parser.parse_args()

    config.DEBUG_MODE = config.DEBUG_MODE or args.verbose
    return args.mode


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



