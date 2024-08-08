import pygame
import math
from queue import PriorityQueue
import sys

# Display Config:
WIDTH = 650
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("A* PathFinder")

# Defining Color Scheme
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GREY = (128, 128, 128)
TURQUOISE = (64, 244, 208)


# This class would draw a 50x50 grid
# This will contain the boxes and the spots
# This spot will hold bunch of different values i.e where it is (row/column)
# The spot should know its width so that it could draw itself
# This will also keep track of its neighbors
# The color will play an important part so that it could determine
# Wether it should be start/ end node barrier or the neighbors


class Spot:
    def __init__(self, row, col, width, total_rows) -> None:
        self.row = row
        self.col = col

        # These will keep track of the (x,y) coordinates on the screen
        self.x = width * row
        self.y = col * width

        self.color = WHITE  # Initial color of cubes/spots
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows

    def get_pos(self):
        return self.row, self.col

    # These contain the squares that have we already looked at or not
    def is_closed(self):
        return self.color == RED

    # Are the spot in the open set or not
    def is_open(self):
        return self.color == GREEN

    # This define the obstacles
    def is_barrier(self):
        return self.color == BLACK

    def is_start(self):
        return self.color == ORANGE

    def is_end(self):
        return self.color == TURQUOISE

    def reset(self):
        return self.color == WHITE

    def make_start(self):
        self.color = ORANGE

    # These contain the squares that have we already looked at or not
    def make_open(self):
        self.color == GREEN

    # Are the spot in the open set or not
    def make_close(self):
        self.color == RED

    def make_barrier(self):
        self.color == BLACK

    def make_end(self):
        self.color = TURQUOISE

    def make_path(self):
        self.color = PURPLE

    # This would draw the Cube/Grid
    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbor(self, grid):
        pass

    def __lt__(self, other):
        return False


# Defining the Hurestic Function H(z):
# p1 & p2 are the point 1 and point 2
# This would also calculate the Manhattan's Distance


def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2

    return abs(x1 - x2) + abs(y1 - y2)


# This would create the Grid
def make_grid(rows, width):
    grid = []
    gap = width // rows  # width of each cubes

    for i in range(rows):
        grid.append([])
        for j in range(rows):
            spot = Spot(i, j, gap, rows)
            grid[i].append(spot)

    return grid


def draw_grid(win, rows, width):

    gap = width // rows

    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))

        for j in range(rows):
            pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))


def draw(win, grid, rows, width):
    win.fill(WHITE)

    for row in grid:
        for spot in row:
            spot.draw(win)

    draw_grid(win, rows, width)
    pygame.display.update()


# This will take care of which box is clicked
# Given a mouse position it will translate that into x,y position
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

    run = True
    started = False

    while run:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                run = False
            if started:
                continue

            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()  # left button
                row, col = get_clicked_pos(pos, ROWS, width)
                spot = grid[row][col]

                if not start:
                    start = spot
                    start.make_start()
                elif not end:
                    end = spot
                    end.make_end()
                elif spot != end and spot != start:
                    spot.make_barrier()

            if pygame.mouse.get_pressed()[2]:
                ...  # left button

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main(WIN, WIDTH)
