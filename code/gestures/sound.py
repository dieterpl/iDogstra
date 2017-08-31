import pygame
import os
from config import config

pygame.mixer.init()
pygame.mixer.music.load(os.path.join(config.SOUNDPATH, "bark.wav"))
pygame.mixer.music.play()
while pygame.mixer.music.get_busy() == True:
    continue