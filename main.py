import pygame
from constants import SCREEN_HEIGHT, SCREEN_WIDTH
from game import Game

def main():
    pygame.mixer.pre_init(frequency=48000, size=-16, channels=2, buffer=1024)
    pygame.init()
    pygame.mixer.set_num_channels(16)
    pygame.mixer.set_reserved(2)
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    print(f"Starting Asteroids with pygame version: {pygame.version.ver}")
    print(f"Screen width: {SCREEN_WIDTH}")
    print(f"Screen height: {SCREEN_HEIGHT}")
    Game(screen).run()

if __name__ == "__main__":
    main()
