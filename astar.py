import pygame
import math
from queue import PriorityQueue
import random

pygame.init()

WIDTH = 600
WIN = pygame.display.set_mode((WIDTH + 200, WIDTH))
pygame.display.set_caption("A* Path Finding Algorithm")

font = pygame.font.Font('freesansbold.ttf', 32)
clock = pygame.time.Clock()

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE= (255, 165, 0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)

class DropDown():

    def __init__(self, color_menu, color_option, x, y, w, h, font, main, options):
        self.color_menu = color_menu
        self.color_option = color_option
        self.rect = pygame.Rect(x, y, w, h)
        self.font = font
        self.main = main
        self.options = options
        self.draw_menu = False
        self.menu_active = False
        self.active_option = -1

    def draw(self, surf):
        pygame.draw.rect(surf, self.color_menu[self.menu_active], self.rect, 0)
        msg = self.font.render(self.main, 1, (0, 0, 0))
        surf.blit(msg, msg.get_rect(center = self.rect.center))

        if self.draw_menu:
            for i, text in enumerate(self.options):
                rect = self.rect.copy()
                rect.y += (i+1) * self.rect.height
                pygame.draw.rect(surf, self.color_option[1 if i == self.active_option else 0], rect, 0)
                msg = self.font.render(text, 1, (0, 0, 0))
                surf.blit(msg, msg.get_rect(center = rect.center))

    def update(self, event_list):
        mpos = pygame.mouse.get_pos()
        self.menu_active = self.rect.collidepoint(mpos)
        
        self.active_option = -1
        for i in range(len(self.options)):
            rect = self.rect.copy()
            rect.y += (i+1) * self.rect.height
            if rect.collidepoint(mpos):
                self.active_option = i
                break

        if not self.menu_active and self.active_option == -1:
            self.draw_menu = False

        for event in event_list:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.menu_active:
                    self.draw_menu = not self.draw_menu
                elif self.draw_menu and self.active_option >= 0:
                    self.draw_menu = False
                    return self.active_option
        return -1


class Spot:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width 
        self.y = col * width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows

    def get_pos(self):
        return self.row, self.col
        
    def is_closed(self):
        return self.color == RED

    def is_open(self):
        return self.color == GREEN

    def is_barrier(self):
        return self.color == BLACK
    
    def is_start(self):
        return self.color == ORANGE

    def is_end(self):
        return self.color == TURQUOISE

    def reset(self):
        self.color = WHITE

    def make_closed(self):
        self.color = RED
    
    def make_open(self):
        self.color = GREEN

    def make_barrier(self):
        self.color = BLACK

    def make_start(self):
        self.color = ORANGE

    def make_end(self):
        self.color = TURQUOISE

    def make_path(self):
        self.color = PURPLE

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        self.neighbors = []
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier(): # DOWN
            self.neighbors.append(grid[self.row + 1][self.col])
            
        if  self.row < self.total_rows - 1 and self.col < self.total_rows - 1 and not grid[self.row + 1][self.col + 1].is_barrier(): # RIGHT
            self.neighbors.append(grid[self.row + 1][self.col + 1])

        if   self.row < self.total_rows - 1 and self.col > 0 and not grid[self.row + 1][self.col - 1].is_barrier(): # LEFT
            self.neighbors.append(grid[self.row + 1][self.col - 1])
        
        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier(): # LEFT
            self.neighbors.append(grid[self.row][self.col - 1])

        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier(): # UP
            self.neighbors.append(grid[self.row - 1][self.col])

        if self.row > 0 and self.col < self.total_rows - 1 and not grid[self.row - 1][self.col + 1].is_barrier(): # RIGHT
            self.neighbors.append(grid[self.row - 1][self.col + 1])
            
        if self.row > 0 and self.col > 0 and not grid[self.row - 1][self.col - 1].is_barrier(): # LEFT
            self.neighbors.append(grid[self.row - 1][self.col - 1])

        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier(): # RIGHT
            self.neighbors.append(grid[self.row][self.col + 1])


    def __lt__(self, other):
        return False


def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    # return abs(x1 - x2) + abs(y1 - y2)
    dist = math.sqrt((x1-x2)*(x1 - x2) + (y1 - y2)*(y1 - y2))
    return dist

def reconstruct_path(came_from, current, start, draw):
    cost = 0
    while current != start:
        # print(current.get_pos())s
        current = came_from[current]
        current.make_path()
        cost += 1
        draw()
    return cost

def astar(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    g_score = {spot: float("inf") for row in grid for spot in row}
    g_score[start] = 0
    f_score = {spot: float("inf") for row in grid for spot in row}
    f_score[start] = h(start.get_pos(), end.get_pos())

    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            cost = reconstruct_path(came_from, end, start, draw)
            end.make_end()
            start.make_start()
            return True

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
            current.make_closed()

    return False

def bfs(draw, grid, start, end):
    came_from = {}
    queue = []
    queue.append(start)
    while queue:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        node = queue.pop(0)

        for neighbor in node.neighbors:
            if not (neighbor.is_closed()) and neighbor not in queue:
                came_from[neighbor] = node
                if neighbor == end:
                    reconstruct_path(came_from, end, start, draw)
                    end.make_end()
                    start.make_start()
                    return True
                queue.append(neighbor)
                neighbor.make_open()

        if node == end:
            reconstruct_path(came_from, end, start, draw)
            end.make_end()
            start.make_start()
            return True

        if node != start:
            node.make_closed()

        draw()

    return False


def dfs(draw, grid, start, end):
    came_from = {}
    queue = []
    queue.append(start)
    while queue:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        node = queue.pop(-1)

        random.shuffle(node.neighbors)
        for neighbor in node.neighbors:
            if not (neighbor.is_closed()) and neighbor not in queue:
                came_from[neighbor] = node
                if neighbor == end:
                    reconstruct_path(came_from, end, start, draw)
                    end.make_end()
                    start.make_start()
                    return True
                queue.append(neighbor)
                neighbor.make_open()

        if node == end:
            reconstruct_path(came_from, end, start, draw)
            end.make_end()
            start.make_start()
            return True

        if node != start:
            node.make_closed()

        draw()

    return False


def make_grid(rows, width):
    grid = []
    gap = width // rows
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



def draw(win, grid, rows, list1, width):
    # clock.tick(15)
    win.fill(WHITE)

    for row in grid:
        for spot in row:
            spot.draw(win)

    draw_grid(win, rows, width)
    list1.draw(win)

    pygame.display.update()


def get_clicked_pos(pos, rows, width):
    gap = width // rows
    y, x = pos
    
    row = y // gap
    col = x // gap

    return row, col


def main(win, width):

    # Drop Down Menu
    COLOR_INACTIVE = (100, 80, 255)
    COLOR_ACTIVE = (100, 200, 255)
    COLOR_LIST_INACTIVE = (255, 100, 100)
    COLOR_LIST_ACTIVE = (255, 150, 150)

    list1 = DropDown(
    [COLOR_INACTIVE, COLOR_ACTIVE],
    [COLOR_LIST_INACTIVE, COLOR_LIST_ACTIVE],
    WIDTH, 0, 200, 50, 
    pygame.font.SysFont(None, 30), 
    "Select Algorithm", ["DFS", "BFS", "A-Star"])

    ROWS = 50
    grid = make_grid(ROWS, width)

    start = None
    end = None

    run = True
    started = False

    while run:
        draw(win, grid, ROWS, list1, width)
        event_list = pygame.event.get()
        for event in event_list:
            if event.type == pygame.QUIT:
                run = False 

            if started:
                continue

            if pygame.mouse.get_pressed()[0] and pygame.mouse.get_pos() < (WIDTH, WIDTH): # Left
                pos = pygame.mouse.get_pos()
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

            elif pygame.mouse.get_pressed()[2] and pygame.mouse.get_pos() < (WIDTH, WIDTH):     # Right   
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                spot = grid[row][col]
                spot.reset()
                if spot == start:
                    start = None
                elif spot == end:
                    end = None             

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not started and start and end:
                    for row in grid:
                        for spot in row:
                            spot.update_neighbors(grid)

                    algo = list1.main
                    if algo == "A-Star":
                        ans = astar(lambda: draw(win, grid, ROWS, list1, width), grid, start, end)
                    elif algo == "DFS":
                        ans = dfs(lambda: draw(win, grid, ROWS, list1, width), grid, start, end)
                    elif algo == "BFS":
                        ans = bfs(lambda: draw(win, grid, ROWS, list1, width), grid, start, end)
                    else:
                        ans = astar(lambda: draw(win, grid, ROWS, list1, width), grid, start, end)
                    print(ans)

                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)
                
                if event.key == pygame.K_r:
                    for row in grid:
                        for spot in row:
                            if not (spot.is_start() or spot.is_end() or spot.is_barrier()):
                                spot.reset()

            selected_option = list1.update(event_list)
            if selected_option >= 0:
                list1.main = list1.options[selected_option]
                
    pygame.quit()


main(WIN, WIDTH)
