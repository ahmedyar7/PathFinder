import pygame
import random
from spots import Spot


class MazeGenerator:
    def __init__(self, rows, width):
        self.rows = rows
        self.width = width
        self.grid = []
        self.starting_point = None

    def make_grid(self):
        block_size = self.width // self.rows
        for i in range(self.rows):
            self.grid.append(
                [Spot(i, j, block_size, self.rows) for j in range(self.rows)]
            )

    def get_neighbors(self, row, col):
        """Get neighbors for a specific cell (up, down, left, right)"""
        neighbors = []
        if row > 1:  # Check UP
            neighbors.append((row - 2, col))
        if row < self.rows - 2:  # Check DOWN
            neighbors.append((row + 2, col))
        if col > 1:  # Check LEFT
            neighbors.append((row, col - 2))
        if col < self.rows - 2:  # Check RIGHT
            neighbors.append((row, col + 2))
        return neighbors

    def generate_maze(self):
        # Step 1: Start with a random point
        start_row = random.randrange(1, self.rows, 2)
        start_col = random.randrange(1, self.rows, 2)
        self.grid[start_row][start_col].make_path()
        self.starting_point = (start_row, start_col)

        # Initialize frontier cells
        frontier_cells = []
        for neighbor in self.get_neighbors(start_row, start_col):
            frontier_cells.append((neighbor, (start_row, start_col)))

        while frontier_cells:
            # Randomly choose a frontier cell
            (frontier_row, frontier_col), (prev_row, prev_col) = random.choice(
                frontier_cells
            )
            frontier_cells.remove(((frontier_row, frontier_col), (prev_row, prev_col)))

            if self.grid[frontier_row][frontier_col].color == (
                255,
                255,
                255,
            ):  # Already path
                continue

            # Mark the new cell as part of the maze
            self.grid[frontier_row][frontier_col].make_path()
            # Break the wall in between
            self.grid[(frontier_row + prev_row) // 2][
                (frontier_col + prev_col) // 2
            ].make_path()

            # Add neighbors of the frontier cell to the frontier list
            for neighbor in self.get_neighbors(frontier_row, frontier_col):
                if self.grid[neighbor[0]][neighbor[1]].color == (
                    0,
                    0,
                    0,
                ):  # Still a wall
                    frontier_cells.append((neighbor, (frontier_row, frontier_col)))

    def draw_maze(self, window):
        for row in self.grid:
            for spot in row:
                spot.draw(window)
        pygame.display.update()
