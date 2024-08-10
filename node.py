RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


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

    def is_started(self):
        return self.color == ORANGE

    def is_ended(self):
        return self.color == PURPLE
