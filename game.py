import pygame
from queue import PriorityQueue
import sys

pygame.init()
RESOLUTION = (1280, 670)
WIN = pygame.display.set_mode(RESOLUTION)
pygame.display.set_caption("A* PathFinder")


def main():
    run = True

    while run:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
