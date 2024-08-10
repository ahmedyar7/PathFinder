RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

import pygame

pygame.init()


class Node:
    def __init__(self, row, col, width, height, total_rows) -> None:
        self.x = row * width
        self.y = height * col
        self.row = row
        self.col = col
        self.total_rows = total_rows
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.height = height

    def get_pos(self):
        return self.row, self.col

    def is_start(self):
        return self.color == ORANGE

    def is_end(self):
        return self.color == PURPLE

    def is_barrier(self):
        return self.color == BLACK

    def is_open(self):
        return self.color == GREEN

    def is_close(self):
        return self.color == RED

    def reset(self):
        return self.color == WHITE

    def make_start(self):
        self.color = ORANGE

    def make_end(self):
        self.color = PURPLE

    def make_barrier(self):
        self.color = BLACK

    def make_open(self):
        self.color = GREEN

    def is_close(self):
        self.color = RED

    def draw(self, res):
        pygame.draw.rect(res, self.color, (self.x, self.y, self.width, self.height))

    def update_neighbors(self):
        pass

    def __lt__(self, other):
        return False
