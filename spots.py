import pygame

CLOSED_NODE = (255, 0, 102)  # Bright Pink
OPEN_NODE = (0, 191, 255)  # DeepSkyBlue
BLUE = (0, 255, 127)  # SpringGreen
BACKGROUND_COLOR = (255, 255, 255)  # Pure White
BARRIER = (0, 0, 0)  # Black
PATH = (255, 255, 0)  # DeepPink
START_NODE = (0, 255, 0)  # Bright Green
END_NODE = (255, 69, 0)  # OrangeRed


WIDTH = 650
WINDOW = pygame.display.set_mode((WIDTH, WIDTH))


class Spot:
    def __init__(self, row, col, width, total_rows) -> None:
        self.row = row
        self.col = col
        self.total_rows = total_rows
        self.width = width
        self.x = width * row
        self.y = col * width
        self.color = BACKGROUND_COLOR
        self.neighbors = []

    def get_pos(self) -> tuple:
        return self.row, self.col

    def is_open(self) -> bool:
        return self.color == OPEN_NODE

    def is_closed(self) -> bool:
        return self.color == CLOSED_NODE

    def is_barrier(self) -> bool:
        return self.color == BARRIER

    def is_start(self) -> bool:
        return self.color == START_NODE

    def is_end(self) -> bool:
        return self.color == END_NODE

    def reset(self):
        self.color = BACKGROUND_COLOR

    def make_open(self):
        self.color = OPEN_NODE

    def make_closed(self):
        self.color = CLOSED_NODE

    def make_barrier(self):
        self.color = BARRIER

    def make_start(self):
        self.color = START_NODE

    def make_end(self):
        self.color = END_NODE

    def make_path(self):
        self.color = PATH

    def draw(self):
        pygame.draw.rect(WINDOW, self.color, (self.x, self.y, self.width, self.width))

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
