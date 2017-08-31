import pygame
import os
from config import config


class Sound:

    def __init__(self):
        pygame.mixer.init()

    def do_sound(self, gesture):
        sound_file = get_sound_from_gesture(gesture)
        if(sound_file != ""):
            pygame.mixer.music.load(os.path.join(config.SOUNDPATH, sound_file))
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                continue

    def get_sound_from_gesture(self, gesture):
        if gesture == "wait" return "snort.wav"  # schnarchen
        elif gesture == "track" return "pant.wav"  # hecheln
        elif gesture == "search" return "whimper.wav"  # fiepen
        elif gesture == "follow" return "bark.wav"  # bellen
        elif gesture == "dodge" return "gnar.wav"  # knurren
        else return ""
