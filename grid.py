import pygame

GREY = (128, 128, 128)
WHITE = (255, 255, 255)


class Grid:
    def __init__(self) -> None:
        pass

    def make_grid(self, rows, width):
        """This will create the 2D array in the form of the grid structur"""
        from spots import Spot

        grid = []
        gap = width // rows
        for i in range(rows):
            grid.append([])
            for j in range(rows):
                spot = Spot(i, j, gap, rows)
                grid[i].append(spot)
        return grid

    def draw_grid(self, win, rows, width):
        """This will draw the grid line for the function"""
        gap = width // rows
        for i in range(rows):
            pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
            for j in range(rows):
                pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))

    def draw(self, win, grid, rows, width):
        """This would actually draw the grid with all the spots and the grid lines"""
        win.fill(WHITE)
        for row in grid:
            for spot in row:
                spot.draw()

        self.draw_grid(win, rows, width)
        pygame.display.update()
