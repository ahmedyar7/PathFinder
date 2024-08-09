import pygame
import sys
import math
from queue import PriorityQueue

# Display Config:
WIDTH = 650
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("A* PathFinder")

# Defining Color Scheme
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
BLACK = (255, 255, 255)
WHITE = (0, 0, 0)
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
        self.color = WHITE

    def make_start(self):
        self.color = ORANGE

    # These contain the squares that have we already looked at or not
    def make_open(self):
        self.color = GREEN

    # Are the spot in the open set or not
    def make_close(self):
        self.color = RED

    def make_barrier(self):
        self.color = BLACK

    def make_end(self):
        self.color = TURQUOISE

    def make_path(self):
        self.color = PURPLE

    # This would draw the Cube/Grid
    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbor(self, grid):
        self.neighbors = []
        if (
            self.row < self.total_rows - 1
            and not grid[self.row + 1][self.col].is_barrier()
        ):  # DOWN
            self.neighbors.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():  # UP
            self.neighbors.append(grid[self.row - 1][self.col])

        if (
            self.col < self.total_rows - 1
            and not grid[self.row][self.col + 1].is_barrier()
        ):  # RIGHT
            self.neighbors.append(grid[self.row][self.col + 1])

        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():  # LEFT
            self.neighbors.append(grid[self.row][self.col - 1])

    def __lt__(self, other):
        return False


# Defining the Hurestic Function H(z):
# p1 & p2 are the point 1 and point 2
# This would also calculate the Manhattan's Distance
def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2

    return abs(x1 - x2) + abs(y1 - y2)


def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()


# This would be the A* Algorithm
def algorithm(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()

    # This would add the start node with it's original f-score i.e 0
    # count is being added so that we can refer when we addded these items
    # So that we can break ties when we have 2 spot having the same f-score

    open_set.put((0, count, start))

    # This will keep track of which node came from which node
    came_from = {}
    g_score = {spot: float("inf") for row in grid for spot in row}
    g_score[start] = 0

    f_score = {spot: float("inf") for row in grid for spot in row}
    f_score[start] = h(start.get_pos(), end.get_pos())

    # This would take care of which items are in the PriorityQueue
    open_set_hash = {start}

    # this would traverse throught all possilbe node
    # and the end the path would exit or it wont exist
    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        # Open set at [2] because the open_set will store f_score, count, start
        # So [2] will be the node
        current = open_set.get()[2]

        # This will pop out the node such that there are no duplicates
        open_set_hash.remove(current)

        # The node we pulled out from priorty queue is end node
        # Then we found the shortest path, construct the path
        if current == end:
            reconstruct_path(came_from, end, draw)
            end.make_end()
            return True

        # Considering neighbors of the current node:
        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())

                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()

        draw()

        if current != start:
            current.make_close()

    return False


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

    while run:
        draw(win, grid, ROWS, width)

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                run = False

            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()  # left button
                row, col = get_clicked_pos(pos, ROWS, width)
                spot = grid[row][col]

                if not start and spot != end:
                    start = spot
                    start.make_start()

                elif not end and spot != start:
                    end = spot
                    end.make_end()

                elif spot != end and spot != start:
                    spot.make_barrier()

            elif pygame.mouse.get_pressed()[2]:  # right button
                pos = pygame.mouse.get_pos()  # left button
                row, col = get_clicked_pos(pos, ROWS, width)
                spot = grid[row][col]
                spot.reset()

                if spot == start:
                    start = None

                elif spot == end:
                    end = None

            # This will make sure the run the algorithm
            # This will also update the neighbors
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for spots in row:
                            spots.update_neighbor(grid)

                    algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)

                if event.key == pygame.K_r:
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main(WIN, WIDTH)
