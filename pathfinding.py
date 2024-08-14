from __future__ import print_function
import heapq, math, itertools
from collections import deque
import pyastar2d

from config import *


def calculate_bird_distance(x1, y1, z1, x2, y2, z2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)


def find_path_pyastar2d(map_array, start, goal):
    path = pyastar2d.astar_path(map_array, start, goal, allow_diagonal=True)
    return path


def bresenham_line(x1, y1, x2, y2):
    """Generates points on a line from (x1, y1) to (x2, y2) using Bresenham's algorithm."""
    points = []
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy
    while True:
        points.append((x1, y1))
        if x1 == x2 and y1 == y2:
            break
        e2 = err * 2
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy
    return points


def bresenham_line_3d(x1, y1, z1, x2, y2, z2):
    """Generate points on a 3D Bresenham line from (x1, y1, z1) to (x2, y2, z2)."""
    points = []
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    dz = abs(z2 - z1)
    xs = 1 if x2 > x1 else -1
    ys = 1 if y2 > y1 else -1
    zs = 1 if z2 > z1 else -1

    # Driving axis is X-axis
    if dx >= dy and dx >= dz:
        p1 = 2 * dy - dx
        p2 = 2 * dz - dx
        while x1 != x2:
            points.append((x1, y1, z1))
            x1 += xs
            if p1 >= 0:
                y1 += ys
                p1 -= 2 * dx
            if p2 >= 0:
                z1 += zs
                p2 -= 2 * dx
            p1 += 2 * dy
            p2 += 2 * dz

    # Driving axis is Y-axis
    elif dy >= dx and dy >= dz:
        p1 = 2 * dx - dy
        p2 = 2 * dz - dy
        while y1 != y2:
            points.append((x1, y1, z1))
            y1 += ys
            if p1 >= 0:
                x1 += xs
                p1 -= 2 * dy
            if p2 >= 0:
                z1 += zs
                p2 -= 2 * dy
            p1 += 2 * dx
            p2 += 2 * dz

    # Driving axis is Z-axis
    else:
        p1 = 2 * dy - dz
        p2 = 2 * dx - dz
        while z1 != z2:
            points.append((x1, y1, z1))
            z1 += zs
            if p1 >= 0:
                y1 += ys
                p1 -= 2 * dz
            if p2 >= 0:
                x1 += xs
                p2 -= 2 * dz
            p1 += 2 * dy
            p2 += 2 * dx

    points.append((x2, y2, z2))
    return points


def get_neighbors(position, state):
    x, y, z = position
    neighbors = [
        (x + 1, y, z),     # Right
        (x - 1, y, z),     # Left
        (x, y + 1, z),     # Down
        (x, y - 1, z),     # Up
        (x + 1, y + 1, z), # Diagonal bottom-right
        (x - 1, y + 1, z), # Diagonal bottom-left
        (x + 1, y - 1, z), # Diagonal top-right
        (x - 1, y - 1, z), # Diagonal top-left
    ]
    # Check for stairs and add them to neighbors if applicable
    logic_tiles = state.maps[Z_DEFAULT+z][LOGIC_TILES_INDEX]
    if logic_tiles:
        current_tile = logic_tiles.get((x, y))
        if current_tile:
            if current_tile.material == "stairs up":
                neighbors.append((x, y, z + 1))
            if current_tile.material == "stairs down":
                neighbors.append((x, y, z - 1))
    
    return neighbors


def movement_cost(current_position, next_position):
    dx = abs(next_position[0] - current_position[0])
    dy = abs(next_position[1] - current_position[1])
    if dx == 0 or dy == 0:
        return 1  # Orthogonal movement cost
    else:
        return 1.5  # Diagonal movement cost


def list_accessible_tiles(character, state=game_state):
    """
    Returns the set of all accessible (not impassable in movement point range) tile objects
    New version integrated with the Character class' movement points
    """
    accessible_tiles = set()
    visited = set()

    movement_points_left = character["base"].movement_points_left
    character_position = (character["logic"].pos_x, character["logic"].pos_y, character["logic"].pos_z)
    
    queue = deque([(character_position, movement_points_left)])  # Start from the character's position with the remaining movement points
    
    while queue:
        current_pos, remaining_points = queue.popleft()
        visited.add(current_pos)
        accessible_tiles.add(current_pos)
        
        if remaining_points <= 0:
            continue  # Stop exploring further if no movement points left
        
        # Explore neighboring tiles
        for neighbor in get_neighbors(current_pos, state):
            x, y, z = neighbor
            if (0 <= x < state.map_width and 0 <= y < state.map_height and
                state.maps[Z_DEFAULT+z][ADDRESS_INDEX] and neighbor not in visited):
                logic_tiles = state.maps[Z_DEFAULT+z][LOGIC_TILES_INDEX]
                if logic_tiles:
                    tile = logic_tiles.get((x, y))
                    if tile and tile.passable:
                        new_points = remaining_points - movement_cost(current_pos, neighbor)
                        if new_points >= 0:
                            queue.append((neighbor, new_points))
    
    return accessible_tiles


# !!!
# !!!

# Jump Point Search inbound!

# !!!
# !!!



########################################################################################
# JUMP-POINT SEARCH
#  Described: https://harablog.wordpress.com/2011/09/07/jump-point-search/
#
# Self-contained version of the jump-point search (jps).
# I chose to use nested functions so that the jps method was self contained, and
# because I wanted to avoid using global variables, which I would have needed because
# I'm calling functions in an order defined by a priority queue.
#
# Using this function: 
#   - use generate_field(...) to create an 2d array denoting which cells are walkable
#   - use jps(...) to get paths.
#   - use get_full_path(...) on the result from jps to get every cell in the path. 
#
# Note: this implementation allows diagonal movement and "corner cutting"
#
# https://github.com/c2huc2hu/jps/blob/master/jps.py
#
# Christopher Chu, 2015-01-29
#
########################################################################################

# Define some constants representing the things that can be in a field.
OBSTACLE = -10
DESTINATION = -2
UNINITIALIZED = -1

DEBUG = False  
VISUAL = True
expanded = [[False for j in range(150)] for i in range(200)]  
visited = [[False for j in range(150)] for i in range(200)]

class FastPriorityQueue():
    """
    Because I don't need threading, I want a faster queue than queue.PriorityQueue
    Implementation copied from: https://docs.python.org/3.3/library/heapq.html
    """
    def __init__(self):
        self.pq = []                         # list of entries arranged in a heap
        self.counter = itertools.count()     # unique sequence count

    def add_task(self, task, priority=0):
        'Add a new task'
        count = next(self.counter)
        entry = [priority, count, task]
        heapq.heappush(self.pq, entry)

    def pop_task(self):
        'Remove and return the lowest priority task. Raise KeyError if empty.'
        while self.pq:
            priority, count, task = heapq.heappop(self.pq)
            return task
        raise KeyError('pop from an empty priority queue')

    def empty(self):
        return len(self.pq) == 0

def generate_field(terrain, walkable_fcn, pad=False):
    """
    Generate a field from any format as long as a function is provided to determine whether a cell is walkable. 

    Parameters
    terrain - a 2d rectangular iterable somehow representing the terrain.
    walkable_fcn - a function that takes a a cell from terrain as an argument and returns whether that cell can be walked on.
    pad - if true, this function sets the outermost layer of the map to obstacles. if not, the function does nothing.

    Returns:
    the field
    """
    field = [[UNINITIALIZED if walkable_fcn(j) else OBSTACLE for j in i] for i in terrain]
    if pad:
        pad_field(field)
    return field 
        
def pad_field(field):
    """
    Fill the outer border of a field with obstacles

    Parameters
    field - a 2d rectangular array with obstacles.

    Returns:
    None
    """
    for i in range(len(field)):
        field[i][0] = OBSTACLE
        field[i][-1] = OBSTACLE
    for j in range(len(field[0])):
        field[0][j] = OBSTACLE
        field[-1][j] = OBSTACLE

def load_obstacle_image(img_name, obstacle_colour=0xFFFFFF):
    """
    Loads a field from an image, where the obstacles are marked. PNG or BMP are the best because they're lossless
    Requires pygame.

    Returns a field that can be used in jps. 
    
    img_name - a filename for a .png or .bmp file. 
    obstacle_colour - the colour that represents obstacles in form 0xABCDEF
    """
    import pygame
    image = pygame.surfarray.array3d(pygame.image.load(img_name))
    obstacle_colour = (obstacle_colour // 0x10000, obstacle_colour // 0x100 % 0x100, obstacle_colour % 0x100)

    return generate_field(image, lambda x:(x!=obstacle_colour).any(), pad=True) 

def load_path_image(img_name, path_colour=0x000000):
    """
    Loads a field from an image where the paths are marked. PNG or BMP are the best.
    This is pretty much the opposite of load_obstacle_image. 
    Requires pygame.

    Returns a field that can be used in jps.

    img_name - a filename for a .png or .bmp file. 
    obstacle_colour - the colour that represents obstacles as an int
    """
    
    import pygame
    image = pygame.surfarray.array3d(pygame.image.load(img_name))
    path_colour = (path_colour // 0x10000, path_colour // 0x100 % 0x100, path_colour % 0x100)

    return generate_field(image, lambda x:(x==path_colour).all(), pad=True)

def jps(field, start_x, start_y, end_x, end_y):
    """
    Run a jump point search on a field with obstacles.
    
    Parameters
    field            - 2d array representing the cost to get to that node.
    start_x, start_y - the x, y coordinates of the starting position (must be ints)
    end_x, end_y     - the x, y coordinates of the destination (must be ints)

    Return:
    a list of tuples corresponding to the jump points. drawing straight lines betwen them gives the path.
    OR
    [] if no path is found. 
    """
    global expanded, visited
    if VISUAL:
        expanded = [[False for j in range(len(field[0]))] for i in range(len(field))]  
        visited = [[False for j in range(len(field[0]))] for i in range(len(field))]  
    
    # handle obvious exception cases: either start or end is unreachable
    if field[start_x][start_y] == OBSTACLE:
        raise ValueError("No path exists: the start node is not walkable")
    if field[end_x][end_y] == OBSTACLE:
        raise ValueError("No path exists: the end node is not walkable")

    try: 
        import queue 
    except:
        import Queue as queue # type: ignore # python 2 compatibility

    class FoundPath(Exception):
        """ Raise this when you found a path. it's not really an error,
        but I need to stop the program and pass it up to the real function"""
        pass

    def queue_jumppoint(node):
        """
        Add a jump point to the priority queue to be searched later. The priority is the minimum possible number of steps to the destination. 
        Also check whether the search is finished.

        Parameters
        pq - a priority queue for the jump point search
        node - 2-tuple with the coordinates of a point to add.

        Return
        None
        """
        if node is not None:
            pq.add_task (node, field [node[0]] [node[1]] + max(abs(node[0] - end_x), abs(node[1] - end_y)))

            
    def _jps_explore_diagonal (startX, startY, directionX, directionY):
        """
        Explores field along the diagonal direction for JPS, starting at point (startX, startY)

        Parameters
        startX, startY - the coordinates to start exploring from. 
        directionX, directionY - an element from: {(1, 1), (-1, 1), (-1, -1), (1, -1)} corresponding to the x and y directions respectively. 

        Return
        A 2-tuple containing the coordinates of the jump point if it found one
        None if no jumppoint was found. 
        """
        cur_x, cur_y = startX, startY #indices of current cell. 
        curCost = field [startX] [startY]

        while (True):
            cur_x += directionX
            cur_y += directionY
            curCost += 1

            if field [cur_x] [cur_y] == UNINITIALIZED:
                field [cur_x] [cur_y] = curCost
                sources [cur_x] [cur_y] = startX, startY
                if VISUAL:
                    visited [cur_x][cur_y] = True
            elif cur_x == end_x and cur_y == end_y:  # destination found
                field [cur_x][cur_y] = curCost
                sources [cur_x] [cur_y] = startX, startY
                if VISUAL:
                    visited[cur_x][cur_y] = True
                raise FoundPath()
            else: #collided with an obstacle. We are done. 
                return None

            # If a jump point is found, 
            if field [cur_x + directionX] [cur_y] == OBSTACLE and field [cur_x + directionX] [cur_y + directionY] != OBSTACLE:
                return (cur_x, cur_y)
            else: #otherwise, extend a horizontal "tendril" to probe the field.
                queue_jumppoint(_jps_explore_cardinal (cur_x, cur_y, directionX, 0))

            if field [cur_x] [cur_y + directionY] == OBSTACLE and field [cur_x + directionX] [cur_y + directionY] != OBSTACLE:
                return (cur_x, cur_y)
            else: #extend a vertical search to look for anything 
                queue_jumppoint(_jps_explore_cardinal (cur_x, cur_y, 0, directionY))

    def _jps_explore_cardinal (startX, startY, directionX, directionY):
        """
        Explores field along a cardinal direction for JPS (north/east/south/west), starting at point (startX, startY)

        Parameters
        startX, startY - the coordinates to start exploring from. 
        directionX, directionY - an element from: {(1, 1), (-1, 1), (-1, -1), (1, -1)} corresponding to the x and y directions respectively. 

        Result: 
        A 2-tuple containing the coordinates of the jump point if it found one
        None if no jumppoint was found.
        """
        cur_x, cur_y = startX, startY #indices of current cell. 
        curCost = field [startX] [startY]

        while (True):
            cur_x += directionX
            cur_y += directionY
            curCost += 1

            if field [cur_x] [cur_y] == UNINITIALIZED:
                field [cur_x][cur_y] = curCost
                sources [cur_x] [cur_y] = startX, startY
                if VISUAL:
                    visited[cur_x][cur_y] = True  
            elif cur_x == end_x and cur_y == end_y:  # destination found
                field [cur_x][cur_y] = curCost
                sources [cur_x] [cur_y] = startX, startY
                if VISUAL:
                    visited[cur_x][cur_y] = True
                raise FoundPath()
            else: #collided with an obstacle or previously explored part. We are done. 
                return None

            #check neighbouring cells, i.e. check if cur_x, cur_y is a jump point. 
            if directionX == 0: 
                if field [cur_x + 1] [cur_y] == OBSTACLE and field [cur_x + 1] [cur_y + directionY] != OBSTACLE:
                    return cur_x, cur_y
                if field [cur_x - 1] [cur_y] == OBSTACLE and field [cur_x - 1] [cur_y + directionY] != OBSTACLE:
                    return cur_x, cur_y
            elif directionY == 0:
                if field [cur_x] [cur_y + 1] == OBSTACLE and field [cur_x + directionX] [cur_y + 1] != OBSTACLE:
                    return cur_x, cur_y
                if field [cur_x] [cur_y - 1] == OBSTACLE and field [cur_x + directionX] [cur_y - 1] != OBSTACLE:
                    return cur_x, cur_y

    # MAIN JPS FUNCTION
    field = [[j for j in i] for i in field]  # this takes less time than deep copying. 

    # Initialize some arrays and certain elements. 
    sources = [[(None, None) for i in field[0]] for j in field]  # the jump-point predecessor to each point.
    field [start_x] [start_y] = 0
    field [end_x] [end_y] = DESTINATION

    pq = FastPriorityQueue()
    queue_jumppoint((start_x, start_y))

    # Main loop: iterate through the queue
    while (not pq.empty()):
        pX, pY = pq.pop_task()

        if VISUAL:
            expanded[pX][pY] = True 
        
        try:
            queue_jumppoint(_jps_explore_cardinal (pX, pY, 1, 0))
            queue_jumppoint(_jps_explore_cardinal (pX, pY, -1, 0))
            queue_jumppoint(_jps_explore_cardinal (pX, pY, 0, 1))
            queue_jumppoint(_jps_explore_cardinal (pX, pY, 0, -1))

            queue_jumppoint(_jps_explore_diagonal (pX, pY, 1, 1))
            queue_jumppoint(_jps_explore_diagonal (pX, pY, 1, -1))
            queue_jumppoint(_jps_explore_diagonal (pX, pY, -1, 1))
            queue_jumppoint(_jps_explore_diagonal (pX, pY, -1, -1))
        except FoundPath:
            return _get_path(sources, start_x, start_y, end_x, end_y)

    raise ValueError("No path is found")
    #end of jps
    

def _get_path(sources, start_x, start_y, end_x, end_y):
    """
    Reconstruct the path from the source information as given by jps(...).

    Parameters
    sources          - a 2d array of the predecessor to each node
    start_x, start_y - the x, y coordinates of the starting position
    end_x, end_y     - the x, y coordinates of the destination
    
    Return
    a list of jump points as 2-tuples (coordinates) starting from the start node and finishing at the end node.
    """
    result = []
    cur_x, cur_y = end_x, end_y
    
    while cur_x != start_x or cur_y != start_y:
        result.append((cur_x, cur_y))
        cur_x, cur_y = sources[cur_x][cur_y]
    result.reverse()
    return [(start_x, start_y)] + result

def _signum(n):
    if n > 0: return 1
    elif n < 0: return -1
    else: return 0

def get_full_path(path):
    """
    Generates the full path from a list of jump points. Assumes that you moved in only one direction between
    jump points.

    Parameters
    path - a path generated by get_path

    Return
    a list of 2-tuples (coordinates) starting from the start node and finishing at the end node.
    """

    if path == []:
        return []
    
    cur_x, cur_y = path[0]
    result = [(cur_x, cur_y)]
    for i in range(len(path) - 1):
        while cur_x != path[i + 1][0] or cur_y != path[i + 1][1]:
            cur_x += _signum(path[i + 1][0] - path[i][0])
            cur_y += _signum(path[i + 1][1] - path[i][1])
            result.append((cur_x, cur_y))
    return result

def drawGrid (field):
    """
    Represent the field as a grid. Pretty much prints out the 2d array, but prints obstacles nicely.

    Parameters
    field - a 2d array with the obstacles and whatever else happens to be in the field. 

    Return
    None
    """
    print ("=======================================")
    for i in field: 
        for j in i:
            if j == OBSTACLE:
                print ("###", end=" ")
            else:
                print ("{:<3}".format(j), end=" ") 
        print("")

def draw_jps(field, path, background=None):
    """
    Draw the output of the latest JPS search

    Background: a filename
    """
    SCROLL_SPEED = 2
    import pygame
    pygame.init()
    window = pygame.display.set_mode ((800, 600))
    main_surface = pygame.Surface ((len(field) * 3, len(field[0]) * 3), flags=pygame.SRCALPHA)
    main_surface.fill((0, 0, 0, 0))

    black_surface = pygame.Surface ((800, 600))
    black_surface.fill(0x000000)
    if background is not None:
        background = pygame.image.load(background)
        background = pygame.transform.scale(background, (background.get_width() * 3, background.get_height() * 3))

    for i in range(len(field)):
        for j in range(len(field[i])):
            if field[i][j] != OBSTACLE:
                pygame.draw.rect(main_surface, (0, 255, 0, 100), (i * 3, j * 3, 3, 3)) #valid path cells are green 
            else:
                pygame.draw.rect(main_surface, (255, 0, 0, 100), (i * 3, j * 3, 3, 3)) #obstacles are red 

##            if visited[i][j]:
##                pygame.draw.rect(main_surface, (100, 50, 50, 100), (i * 3, j * 3, 3, 3))  # this could draw the visited cells, but it messes up the transparencies
                
            if expanded[i][j]:
                pygame.draw.rect(main_surface, (0, 100, 100, 255), (i * 3, j * 3, 3, 3))   #expanded cells are periwinkle
    for i in path:
        pygame.draw.rect(main_surface, (255, 0, 255, 255), (i[0] * 3 + 1, i[1] * 3 + 1, 2, 2))  # path is magenta

    offset_x, offset_y = 0, 0
    while(True):
        #handle events
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                quit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE:
                    offset_x, offset_y = 0, 0

        
        #handle key events
        key_events = pygame.key.get_pressed()
        if key_events [pygame.K_LEFT] or key_events [pygame.K_a]:
            offset_x += SCROLL_SPEED
        if key_events [pygame.K_RIGHT] or key_events [pygame.K_d]:
            offset_x -= SCROLL_SPEED
        if key_events [pygame.K_UP] or key_events [pygame.K_w]:
            offset_y += SCROLL_SPEED
        if key_events [pygame.K_DOWN] or key_events [pygame.K_s]:
            offset_y -= SCROLL_SPEED

        window.blit(black_surface, (0, 0))
        if background is not None:
            window.blit(background, (offset_x, offset_y))
        window.blit(main_surface, (offset_x, offset_y))
        pygame.display.flip()

# Turn visual and debug modes on/ off
def set_visual(val):
    global VISUAL
    VISUAL = val
def set_debug(val):
    global DEBUG
    DEBUG = val    





















# import math, time, heapq


# def heuristic(a, b, hchoice):
#     if hchoice == 1:
#         xdist = math.fabs(b[0] - a[0])
#         ydist = math.fabs(b[1] - a[1])
#         if xdist > ydist:
#             return 14 * ydist + 10 * (xdist - ydist)
#         else:
#             return 14 * xdist + 10 * (ydist - xdist)
#     if hchoice == 2:
#         return math.sqrt((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2)


# def blocked(cX, cY, dX, dY, matrix):
#     if cX + dX < 0 or cX + dX >= matrix.shape[0]:
#         return True
#     if cY + dY < 0 or cY + dY >= matrix.shape[1]:
#         return True
#     if dX != 0 and dY != 0:
#         if matrix[cX + dX][cY] == 1 and matrix[cX][cY + dY] == 1:
#             return True
#         if matrix[cX + dX][cY + dY] == 1:
#             return True
#     else:
#         if dX != 0:
#             if matrix[cX + dX][cY] == 1:
#                 return True
#         else:
#             if matrix[cX][cY + dY] == 1:
#                 return True
#     return False


# def dblock(cX, cY, dX, dY, matrix):
#     if matrix[cX - dX][cY] == 1 and matrix[cX][cY - dY] == 1:
#         return True
#     else:
#         return False


# def direction(cX, cY, pX, pY):
#     dX = int(math.copysign(1, cX - pX))
#     dY = int(math.copysign(1, cY - pY))
#     if cX - pX == 0:
#         dX = 0
#     if cY - pY == 0:
#         dY = 0
#     return (dX, dY)


# def nodeNeighbours(cX, cY, parent, matrix):
#     neighbours = []
#     if type(parent) != tuple:
#         for i, j in [
#             (-1, 0),
#             (0, -1),
#             (1, 0),
#             (0, 1),
#             (-1, -1),
#             (-1, 1),
#             (1, -1),
#             (1, 1),
#         ]:
#             if not blocked(cX, cY, i, j, matrix):
#                 neighbours.append((cX + i, cY + j))

#         return neighbours
#     dX, dY = direction(cX, cY, parent[0], parent[1])

#     if dX != 0 and dY != 0:
#         if not blocked(cX, cY, 0, dY, matrix):
#             neighbours.append((cX, cY + dY))
#         if not blocked(cX, cY, dX, 0, matrix):
#             neighbours.append((cX + dX, cY))
#         if (
#             not blocked(cX, cY, 0, dY, matrix)
#             or not blocked(cX, cY, dX, 0, matrix)
#         ) and not blocked(cX, cY, dX, dY, matrix):
#             neighbours.append((cX + dX, cY + dY))
#         if blocked(cX, cY, -dX, 0, matrix) and not blocked(
#             cX, cY, 0, dY, matrix
#         ):
#             neighbours.append((cX - dX, cY + dY))
#         if blocked(cX, cY, 0, -dY, matrix) and not blocked(
#             cX, cY, dX, 0, matrix
#         ):
#             neighbours.append((cX + dX, cY - dY))

#     else:
#         if dX == 0:
#             if not blocked(cX, cY, dX, 0, matrix):
#                 if not blocked(cX, cY, 0, dY, matrix):
#                     neighbours.append((cX, cY + dY))
#                 if blocked(cX, cY, 1, 0, matrix):
#                     neighbours.append((cX + 1, cY + dY))
#                 if blocked(cX, cY, -1, 0, matrix):
#                     neighbours.append((cX - 1, cY + dY))

#         else:
#             if not blocked(cX, cY, dX, 0, matrix):
#                 if not blocked(cX, cY, dX, 0, matrix):
#                     neighbours.append((cX + dX, cY))
#                 if blocked(cX, cY, 0, 1, matrix):
#                     neighbours.append((cX + dX, cY + 1))
#                 if blocked(cX, cY, 0, -1, matrix):
#                     neighbours.append((cX + dX, cY - 1))
#     return neighbours


# def jump(cX, cY, dX, dY, matrix, goal):

#     nX = cX + dX
#     nY = cY + dY
#     if blocked(nX, nY, 0, 0, matrix):
#         return None

#     if (nX, nY) == goal:
#         return (nX, nY)

#     oX = nX
#     oY = nY

#     if dX != 0 and dY != 0:
#         while True:
#             if (
#                 not blocked(oX, oY, -dX, dY, matrix)
#                 and blocked(oX, oY, -dX, 0, matrix)
#                 or not blocked(oX, oY, dX, -dY, matrix)
#                 and blocked(oX, oY, 0, -dY, matrix)
#             ):
#                 return (oX, oY)

#             if (
#                 jump(oX, oY, dX, 0, matrix, goal) != None
#                 or jump(oX, oY, 0, dY, matrix, goal) != None
#             ):
#                 return (oX, oY)

#             oX += dX
#             oY += dY

#             if blocked(oX, oY, 0, 0, matrix):
#                 return None

#             if dblock(oX, oY, dX, dY, matrix):
#                 return None

#             if (oX, oY) == goal:
#                 return (oX, oY)
#     else:
#         if dX != 0:
#             while True:
#                 if (
#                     not blocked(oX, nY, dX, 1, matrix)
#                     and blocked(oX, nY, 0, 1, matrix)
#                     or not blocked(oX, nY, dX, -1, matrix)
#                     and blocked(oX, nY, 0, -1, matrix)
#                 ):
#                     return (oX, nY)

#                 oX += dX

#                 if blocked(oX, nY, 0, 0, matrix):
#                     return None

#                 if (oX, nY) == goal:
#                     return (oX, nY)

#         else:
#             while True:
#                 if (
#                     not blocked(nX, oY, 1, dY, matrix)
#                     and blocked(nX, oY, 1, 0, matrix)
#                     or not blocked(nX, oY, -1, dY, matrix)
#                     and blocked(nX, oY, -1, 0, matrix)
#                 ):
#                     return (nX, oY)

#                 oY += dY

#                 if blocked(nX, oY, 0, 0, matrix):
#                     return None

#                 if (nX, oY) == goal:
#                     return (nX, oY)

#     return jump(nX, nY, dX, dY, matrix, goal)


# def identifySuccessors(cX, cY, came_from, matrix, goal):
#     successors = []
#     neighbours = nodeNeighbours(cX, cY, came_from.get((cX, cY), 0), matrix)

#     for cell in neighbours:
#         dX = cell[0] - cX
#         dY = cell[1] - cY

#         jumpPoint = jump(cX, cY, dX, dY, matrix, goal)

#         if jumpPoint != None:
#             successors.append(jumpPoint)

#     return successors


# def method(matrix, start, goal, hchoice):

#     came_from = {}
#     close_set = set()
#     gscore = {start: 0}
#     fscore = {start: heuristic(start, goal, hchoice)}

#     pqueue = []

#     heapq.heappush(pqueue, (fscore[start], start))

#     starttime = time.time()

#     while pqueue:

#         current = heapq.heappop(pqueue)[1]
#         if current == goal:
#             data = []
#             while current in came_from:
#                 data.append(current)
#                 current = came_from[current]
#             data.append(start)
#             data = data[::-1]
#             endtime = time.time()
#             #print(gscore[goal])
#             return (data, round(endtime - starttime, 6))

#         close_set.add(current)

#         successors = identifySuccessors(
#             current[0], current[1], came_from, matrix, goal
#         )

#         for successor in successors:
#             jumpPoint = successor

#             if (
#                 jumpPoint in close_set
#             ):  # and tentative_g_score >= gscore.get(jumpPoint,0):
#                 continue

#             tentative_g_score = gscore[current] + length(
#                 current, jumpPoint, hchoice
#             )

#             if tentative_g_score < gscore.get(
#                 jumpPoint, 0
#             ) or jumpPoint not in [j[1] for j in pqueue]:
#                 came_from[jumpPoint] = current
#                 gscore[jumpPoint] = tentative_g_score
#                 fscore[jumpPoint] = tentative_g_score + heuristic(
#                     jumpPoint, goal, hchoice
#                 )
#                 heapq.heappush(pqueue, (fscore[jumpPoint], jumpPoint))
#         endtime = time.time()
#     return (0, round(endtime - starttime, 6))


# def length(current, jumppoint, hchoice):
#     dX, dY = direction(current[0], current[1], jumppoint[0], jumppoint[1])
#     dX = math.fabs(dX)
#     dY = math.fabs(dY)
#     lX = math.fabs(current[0] - jumppoint[0])
#     lY = math.fabs(current[1] - jumppoint[1])
#     if hchoice == 1:
#         if dX != 0 and dY != 0:
#             length = lX * 14
#             return length
#         else:
#             length = (dX * lX + dY * lY) * 10
#             return length
#     if hchoice == 2:
#         return math.sqrt(
#             (current[0] - jumppoint[0]) ** 2 + (current[1] - jumppoint[1]) ** 2
#         )

