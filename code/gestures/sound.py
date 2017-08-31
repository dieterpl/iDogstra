import pygame
import os
from config import config


class Sound:

    def __init__(self):
        pygame.mixer.init()
        self.sounds = {
            "wait": "snort.wav",  # schnarchen
            "track": "pant.wav",  # hecheln
            "search": "whimper.wav",  # fiepen
            "follow": "bark.wav",  # bellen
            "dodge": "gnar.wav",  # knurren
        }

    def do_sound(self, gesture):
        sound_file = self.sounds.get(gesture, "")
        if(sound_file != ""):
            pygame.mixer.music.load(os.path.join(config.SOUNDPATH, sound_file))
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                continue
