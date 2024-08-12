import pygame
import math
import sys
from queue import PriorityQueue
from algorithm import hurestic_function
from grid import make_grid, draw

pygame.init()

WIDTH = 650
WINDOW = pygame.display.set_mode((WIDTH, WIDTH))

pygame.display.set_caption("A-Star-Pathfinder")

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 255, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
TURQUOISE = (64, 224, 208)


class Spot:
    def __init__(self, row, col, width, total_rows) -> None:
        self.row = row
        self.col = col
        self.total_rows = total_rows
        self.width = width
        self.x = width * row
        self.y = col * width
        self.color = WHITE
        self.neighbors = []

    def get_pos(self):
        return self.row, self.col

    def is_open(self):
        return self.color == GREEN

    def is_closed(self):
        return self.color == RED

    def is_barrier(self):
        return self.color == BLACK

    def is_start(self):
        return self.color == ORANGE

    def is_end(self):
        return self.color == TURQUOISE

    def reset(self):
        self.color = WHITE

    def make_open(self):
        self.color = GREEN

    def make_closed(self):
        self.color = RED

    def make_barrier(self):
        self.color = BLACK

    def make_start(self):
        self.color = ORANGE

    def make_end(self):
        self.color = TURQUOISE

    def make_path(self):
        self.color = PURPLE

    def draw(self):
        pygame.draw.rect(WINDOW, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid): ...

    def __lt__(self, other):
        return False


def get_clicked_pos(pos, rows, width):
    gap = width // rows
    y, x = pos

    row = y // gap
    col = x // gap

    return row, col


def main(win, width):

    ROWS = 50
    grid = make_grid(ROWS, width)

    start = None
    end = None

    started = False
    run = True
    while run:
        draw(win, grid, ROWS, width)

        for events in pygame.event.get():
            if events.type == pygame.QUIT:
                run = False
            if started:
                continue

            if pygame.mouse.get_pressed()[0]:  # Left Btn
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                spot = grid[row][col]
                if not start and spot != end:
                    start = spot
                    start.make_start()
                elif not end and spot != start:
                    end = spot
                    end.make_end()
                elif spot != start and spot != end:
                    spot.make_barrier()

            elif pygame.mouse.get_pressed()[2]:  # Right btn
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                spot = grid[row][col]
                spot.reset()

                if spot == start:
                    start = None
                elif spot == end:
                    end = None

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main(WINDOW, WIDTH)
