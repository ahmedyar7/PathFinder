from queue import PriorityQueue
from collections import deque
import heapq
import pygame


class Algorithm:
    def __init__(self) -> None:
        pass

    def hurestic_function(self, p1, p2):
        """
        This willl be the hurestic function that would provide the
        estimation of the distance b/w the nodes
        """

        x1, y1 = p1
        x2, y2 = p2

        return abs(x1 - x2) + abs(y1 - y2)

    def reconstruct_path(self, came_from, current, draw):
        while current in came_from:
            current = came_from[current]
            current.make_path()
            draw()

    def dijkstra_algorithm(self, draw, grid, start, end):
        """This is Dijkstra's Algorithm for pathfinding"""

        # Priority queue for the nodes to be explored
        pq = [(0, start)]
        came_from = {}
        distances = {spot: float("inf") for row in grid for spot in row}
        distances[start] = 0
        visited = set()

        while pq:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

            current_distance, current_spot = heapq.heappop(pq)

            if current_spot in visited:
                continue

            visited.add(current_spot)

            if current_spot == end:
                self.reconstruct_path(came_from, end, draw)
                end.make_end()
                return True

            for neighbor in current_spot.neighbors:
                new_distance = current_distance + 1  # The cost for each step is 1

                if new_distance < distances[neighbor]:
                    came_from[neighbor] = current_spot
                    distances[neighbor] = new_distance
                    heapq.heappush(pq, (new_distance, neighbor))
                    neighbor.make_open()

            draw()

            if current_spot != start:
                current_spot.make_closed()

        return False

    def prim_algorithm(self, draw, grid, start, end):
        """This is an adaptation of Prim's Algorithm for pathfinding"""

        # Initialize the priority queue (min-heap) and visited set
        min_heap = [(0, start)]
        came_from = {}
        visited = {spot: False for row in grid for spot in row}
        visited[start] = True

        while min_heap:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

            current_cost, current = heapq.heappop(min_heap)

            if current == end:
                self.reconstruct_path(came_from, end, draw)
                end.make_end()
                return True

            for neighbor in current.neighbors:
                if not visited[neighbor]:
                    visited[neighbor] = True
                    came_from[neighbor] = current
                    heapq.heappush(
                        min_heap, (1, neighbor)
                    )  # The cost is 1 for unweighted

                    neighbor.make_open()

            draw()

            if current != start:
                current.make_closed()

        return False

    def bfs_algorithm(self, draw, grid, start, end):
        """This is the BFS Algorithm for pathfinding"""

        queue = deque([start])
        came_from = {}
        visited = {spot: False for row in grid for spot in row}
        visited[start] = True

        while queue:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

            current = queue.popleft()

            if current == end:
                self.reconstruct_path(came_from, end, draw)
                end.make_end()
                return True

            for neighbor in current.neighbors:
                if not visited[neighbor]:
                    came_from[neighbor] = current
                    queue.append(neighbor)
                    visited[neighbor] = True
                    neighbor.make_open()

            draw()

            if current != start:
                current.make_closed()

        return False

    def a_star_algorithm(self, draw, grid, start, end):
        """This would be the actual A*Algorithm for the path finding"""

        count = 0

        open_set = PriorityQueue()
        open_set.put((0, count, start))
        came_from = {}
        g_score = {spot: float("inf") for row in grid for spot in row}
        g_score[start] = 0
        f_score = {spot: float("inf") for row in grid for spot in row}
        f_score[start] = self.hurestic_function(start.get_pos(), end.get_pos())
        open_set_hash = {start}

        while not open_set.empty():
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

            current = open_set.get()[2]
            open_set_hash.remove(current)

            if current == end:
                self.reconstruct_path(came_from, current, draw)
                end.make_end()
                return True

            for neighbor in current.neighbors:
                temp_g_score = g_score[current] + 1
                if temp_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = temp_g_score
                    f_score[neighbor] = temp_g_score + self.hurestic_function(
                        neighbor.get_pos(), end.get_pos()
                    )
                    if neighbor not in open_set_hash:
                        count += 1
                        open_set.put((f_score[neighbor], count, neighbor))
                        open_set_hash.add(neighbor)
                        neighbor.make_open()

            draw()

            if current != start:
                current.make_closed()

        return False
