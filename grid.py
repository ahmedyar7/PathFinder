from node import Node
import pygame

GREY = (128, 128, 128)
WHITE = (255, 255, 255)
pygame.init()


class Grid:
    def __init__(self, row, width, height) -> None:
        self.row = row
        self.width = width
        self.height = height
        self.node = Node()

    def make_grid(self) -> list:
        grid = []
        gap = (self.width // self.row) + (self.height // self.row)
        for i in range(self.row):
            grid.append([])
            for j in range(self.row):
                self.node = Node(i, j, gap, self.row)
                grid[i].append(self.node)

        return grid

    def draw_grid(self, win) -> None:
        gap = self.width // self.row
        for i in range(self.row):
            pygame.draw.line(win, GREY, (0, i * gap), (self.width, i * gap))
            for j in range(self.row):
                pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, self.width))

    def draw(self, win, grid):
        win.fill(WHITE)

        for row in grid:
            ...
