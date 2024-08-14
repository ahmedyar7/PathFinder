import pygame
import math
import sys

from algorithm import Algorithm
from grid import Grid


WIDTH = 650
WINDOW = pygame.display.set_mode((WIDTH, WIDTH))

pygame.display.set_caption("A-Star-Pathfinder")


class Program:
    def __init__(self) -> None:
        pygame.init()
        self.algo = Algorithm()
        self.grids = Grid()
        self.driver(WINDOW, WIDTH)

    def get_clicked_pos(self, pos, rows, width):
        gap = width // rows
        y, x = pos

        row = y // gap
        col = x // gap

        return row, col

    def driver(self, win, width):

        ROWS = 50
        grid = self.grids.make_grid(ROWS, width)

        start = None
        end = None

        started = False
        run = True
        while run:
            self.grids.draw(win, grid, ROWS, width)

            for events in pygame.event.get():
                if events.type == pygame.QUIT:
                    run = False
                if started:
                    continue

                if pygame.mouse.get_pressed()[0]:  # Left Btn
                    pos = pygame.mouse.get_pos()
                    row, col = self.get_clicked_pos(pos, ROWS, width)
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
                    row, col = self.get_clicked_pos(pos, ROWS, width)
                    spot = grid[row][col]
                    spot.reset()
                    if spot == start:
                        start = None
                    elif spot == end:
                        end = None

                if events.type == pygame.KEYDOWN:
                    if events.key == pygame.K_SPACE and not started:
                        for row in grid:
                            for spot in row:
                                spot.update_neighbor(grid)

                        self.algo.a_star_algorithm(
                            lambda: self.grids.draw(win, grid, ROWS, width),
                            grid,
                            start,
                            end,
                        )

                    if events.key == pygame.K_b and not started:
                        for row in grid:
                            for spot in row:
                                spot.update_neighbor(grid)

                        self.algo.bfs_algorithm(
                            lambda: self.grids.draw(win, grid, ROWS, width),
                            grid,
                            start,
                            end,
                        )

                    if events.key == pygame.K_p and not started:
                        for row in grid:
                            for spot in row:
                                spot.update_neighbor(grid)

                        self.algo.prim_algorithm(
                            lambda: self.grids.draw(win, grid, ROWS, width),
                            grid,
                            start,
                            end,
                        )

                    if events.key == pygame.K_d and not started:
                        for row in grid:
                            for spot in row:
                                spot.update_neighbor(grid)

                        self.algo.dijkstra_algorithm(
                            lambda: self.grids.draw(win, grid, ROWS, width),
                            grid,
                            start,
                            end,
                        )

                    if events.key == pygame.K_r:
                        start = None
                        end = None
                        grid = self.grids.make_grid(ROWS, width)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    program = Program()
