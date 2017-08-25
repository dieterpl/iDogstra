import image
import time

class ScreenDog:
    def __init__(self):
        self.DEFAULT="test"

    def changeKeyEvent(self):
        return 0

 
if __name__ == '__main__':
    try:
        image = Image.open('neutral.jpg')
        image.show()

        # Beim Abbruch durch STRG+C resetten
    except KeyboardInterrupt:
        print("Messung vom User gestoppt")
    
    

