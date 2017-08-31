import pygame
import os
from config import config


class Sound:

    def __init__(self):
        pygame.mixer.init()

    def bark(self):
        try:
            pygame.mixer.music.load(os.path.join(config.SOUNDPATH, "bark.wav"))
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                continue
        except KeyboardInterrupt:
            print('exit')
