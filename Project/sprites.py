import pygame
import os
import config
import math


class BaseSprite(pygame.sprite.Sprite):
    images = dict()

    def __init__(self, row, col, file_name, transparent_color=None):
        pygame.sprite.Sprite.__init__(self)
        if file_name in BaseSprite.images:
            self.image = BaseSprite.images[file_name]
        else:
            self.image = pygame.image.load(os.path.join(config.IMG_FOLDER, file_name)).convert()
            self.image = pygame.transform.scale(self.image, (config.TILE_SIZE, config.TILE_SIZE))
            BaseSprite.images[file_name] = self.image
        # making the image transparent (if needed)
        if transparent_color:
            self.image.set_colorkey(transparent_color)
        self.rect = self.image.get_rect()
        self.rect.topleft = (col * config.TILE_SIZE, row * config.TILE_SIZE)
        self.row = row
        self.col = col


class Agent(BaseSprite):
    def __init__(self, row, col, file_name):
        super(Agent, self).__init__(row, col, file_name, config.DARK_GREEN)

    def move_towards(self, row, col):
        row = row - self.row
        col = col - self.col
        self.rect.x += col
        self.rect.y += row

    def place_to(self, row, col):
        self.row = row
        self.col = col
        self.rect.x = col * config.TILE_SIZE
        self.rect.y = row * config.TILE_SIZE

    # game_map - list of lists of elements of type Tile
    # goal - (row, col)
    # return value - list of elements of type Tile
    def get_agent_path(self, game_map, goal):
        pass


class ExampleAgent(Agent):
    def __init__(self, row, col, file_name):
        super().__init__(row, col, file_name)

    def get_agent_path(self, game_map, goal):
        path = [game_map[self.row][self.col]]

        row = self.row
        col = self.col
        while True:
            if row != goal[0]:
                row = row + 1 if row < goal[0] else row - 1
            elif col != goal[1]:
                col = col + 1 if col < goal[1] else col - 1
            else:
                break
            path.append(game_map[row][col])
        return path


class Aki(Agent):     # DFS
    def __init__(self, row, col, file_name):
        super().__init__(row, col, file_name)

    def get_agent_path(self, game_map, goal):
        path = [game_map[self.row][self.col]]

        def cost_sort(e):
            return e['cost']

        active_list = []
        neighbors = []
        equal_neighbors = []
        stack_of_neighbors = []

        row = self.row
        col = self.col
        current = [row, col]

        north = [-1, 0]
        east = [0, 1]
        south = [1, 0]
        west = [0, -1]

        max_row = len(game_map) - 1
        max_col = len(game_map[0]) - 1

        while True:
            north[0] = current[0] - 1
            north[1] = current[1]
            east[0] = current[0]
            east[1] = current[1] + 1
            south[0] = current[0] + 1
            south[1] = current[1]
            west[0] = current[0]
            west[1] = current[1] - 1

            # collecting neighbors
            if (current[0] != goal[0] or current[1] != goal[1]) and current not in active_list:
                active_list.append(current)
                neighbors.clear()
                equal_neighbors.clear()
                # north
                if (row - 1) >= 0 and [row - 1, col] not in active_list:
                    neighbors.append({'position': [row - 1, col], 'cost': game_map[row - 1][col].cost(), 'side': 'n'})

                # east
                if (col + 1) <= max_col and [row, col + 1] not in active_list:
                    neighbors.append({'position': [row, col + 1], 'cost': game_map[row][col + 1].cost(), 'side': 'e'})

                # south
                if (row + 1) <= max_row and [row + 1, col] not in active_list:
                    neighbors.append({'position': [row + 1, col], 'cost': game_map[row + 1][col].cost(), 'side': 's'})

                # west
                if (col - 1) >= 0 and [row, col - 1] not in active_list:
                    neighbors.append({'position': [row, col - 1], 'cost': game_map[row][col - 1].cost(), 'side': 'w'})

                # neighbours collected -> sort them
                neighbors.sort(key=cost_sort)
                for i in range(len(neighbors)):
                    stack_of_neighbors.insert(i, {'n': current, 'pos': neighbors[i], 'v': 0})

                # checking if there is equal costs
                if len(neighbors) > 0:
                    equal_neighbors.append(neighbors[0])
                    for i in range(1, len(neighbors)):
                        if neighbors[i]['cost'] == neighbors[0]['cost']:
                            equal_neighbors.append(neighbors[i])

                    if len(equal_neighbors) > 1:

                        # for i in range(len(equal_neighbors) - 1):
                        #     for j in range(i + 1, len(equal_neighbors)):
                        #         pos_side = equal_neighbors[i]['side']
                        #         pos = equal_neighbors[i]['position']
                        #
                        #         if pos_side == 'n' and i == 0:
                        #             row = pos[0]
                        #             col = pos[1]
                        #         elif pos_side == 'n' and i > 0:
                        #             row = pos[0]
                        #             col = pos[1]
                        #             pom = equal_neighbors[i]
                        #             equal_neighbors[i] = equal_neighbors[j]
                        #             equal_neighbors[j] = pom
                        #         elif pos_side == 'e' and (equal_neighbors[0]['side'] != 'n' and equal_neighbors[0]['side'] != 'e'):
                        #             row = pos[0]
                        #             col = pos[1]
                        #             pom = equal_neighbors[i]
                        #             equal_neighbors[i] = equal_neighbors[j]
                        #             equal_neighbors[j] = pom
                        #         elif pos_side == 's' and equal_neighbors[0]['side'] == 'w':
                        #             row = pos[0]
                        #             col = pos[1]
                        #             pom = equal_neighbors[i]
                        #             equal_neighbors[i] = equal_neighbors[j]
                        #             equal_neighbors[j] = pom
                        #         elif (equal_neighbors[0]['side'] != 'n' and equal_neighbors[0]['side'] != 'e' and equal_neighbors[0]['side'] != 's'):
                        #             row = pos[0]
                        #             col = pos[1]
                        #             pom = equal_neighbors[i]
                        #             equal_neighbors[i] = equal_neighbors[j]
                        #             equal_neighbors[j] = pom
                        # change stack too
                        stack_of_neighbors.remove({'n': current, 'pos': equal_neighbors[0], 'v': 0})
                        new = equal_neighbors.pop(0)
                        row = new['position'][0]
                        col = new['position'][1]
                    else:
                        pos = neighbors[0]['position']
                        stack_of_neighbors.remove({'n': current, 'pos': neighbors[0], 'v': 0})
                        row = pos[0]
                        col = pos[1]

                        neighbors.pop(0)

            # vec smo prosli izabrani cvor -> biramo drugi
            elif current[0] != goal[0] or current[1] != goal[1]:
                if len(equal_neighbors) > 1:
                    new_pos = equal_neighbors[0]['position']
                    row = new_pos[0]
                    col = new_pos[1]
                    equal_neighbors.pop(0)
                elif len(neighbors) > 0:
                    new_pos = neighbors[0]['position']
                    row = new_pos[0]
                    col = new_pos[1]
                    neighbors.pop(0)
                else:
                    new_current = stack_of_neighbors.pop(0)
                    row = new_current['pos']['position'][0]
                    col = new_current['pos']['position'][1]
                    ind = active_list.index(new_current['n'])
                    for i in range(len(active_list) - ind - 1):
                        active_list.pop()

            else:
                active_list.append(current)
                break

            current = [row, col]

        for i in range(1, len(active_list)):
            path.append(game_map[active_list[i][0]][active_list[i][1]])
        return path


class Jocke(Agent):     # BFS
    def __init__(self, row, col, file_name):
        super().__init__(row, col, file_name)

    def get_agent_path(self, game_map, goal):
        path = [game_map[self.row][self.col]]

        def cost_sort(e):
            return e['average']

        active_list = []
        neighbors = []
        list_of_neighbors = []
        equal_neighbors = []
        stack_of_neighbors = []

        row = self.row
        col = self.col
        current = {'position': [row, col], 'path': []}

        north = [-1, 0]
        east = [0, 1]
        south = [1, 0]
        west = [0, -1]

        max_row = len(game_map) - 1
        max_col = len(game_map[0]) - 1
        aver_num = 0

        def average(n, a_list):
            # aver_num = 0
            for br in range(len(n)):
                list_of_neighbors.clear()
                p = n[br]['position']
                if p not in a_list:
                    # north
                    if p[0] - 1 >= 0 and [p[0] - 1, p[1]] not in a_list:
                        list_of_neighbors.append(
                            {'n': p, 'my_position': [p[0] - 1, p[1]], 'cost': game_map[p[0] - 1][p[1]].cost(), 's': 'n'})
                    # east
                    if (p[1] + 1) <= max_col and [p[0], p[1] + 1] not in a_list:
                        list_of_neighbors.append(
                            {'n': p, 'my_position': [p[0], p[1] + 1], 'cost': game_map[p[0]][p[1] + 1].cost(), 's': 'e'})
                    #south
                    if (p[0] + 1) <= max_row and [p[0] + 1, p[1]] not in a_list:
                        list_of_neighbors.append(
                            {'n': p, 'my_position': [p[0] + 1, p[1]], 'cost': game_map[p[0] + 1][p[1]].cost(), 's': 's'})
                    # west
                    if (p[1] - 1) >= 0 and [p[0], p[1] - 1] not in a_list:
                        list_of_neighbors.append(
                            {'n': p, 'my_position': [p[0], p[1] - 1], 'cost': game_map[p[0]][p[1] - 1].cost(), 's': 'w'})

                if len(list_of_neighbors) > 0:
                    n[br]['average'] = -1
                    for li in range(len(list_of_neighbors)):
                        # if n[br]['position'][0] == goal[0] and n[br]['position'][1] == goal[1]:
                        #     n[br]['average'] == -100
                        #     break
                        # else:
                        if n[br]['average'] == -1:
                            n[br]['average'] = list_of_neighbors[li]['cost']
                        else:
                            n[br]['average'] = n[br]['average'] + list_of_neighbors[li]['cost']
                    n[br]['average'] = n[br]['average']/len(list_of_neighbors)
                else:
                    n[br]['average'] = 100000

        while True:
            north[0] = current['position'][0] - 1
            north[1] = current['position'][1]
            east[0] = current['position'][0]
            east[1] = current['position'][1] + 1
            south[0] = current['position'][0] + 1
            south[1] = current['position'][1]
            west[0] = current['position'][0]
            west[1] = current['position'][1] - 1

            active_list = current['path']

            # collecting neighbors
            if (current['position'][0] != goal[0] or current['position'][1] != goal[1]) and current['position'] not in active_list:
                active_list.append(current['position'])
                neighbors.clear()
                equal_neighbors.clear()
                # north
                if (row - 1) >= 0 and [row - 1, col] not in active_list:
                    neighbors.append({'position': [row - 1, col], 'cost': game_map[row - 1][col].cost(), 'side': 'n'})

                # east
                if (col + 1) <= max_col and [row, col + 1] not in active_list:
                    neighbors.append({'position': [row, col + 1], 'cost': game_map[row][col + 1].cost(), 'side': 'e'})

                # south
                if (row + 1) <= max_row and [row + 1, col] not in active_list:
                    neighbors.append({'position': [row + 1, col], 'cost': game_map[row + 1][col].cost(), 'side': 's'})

                # west
                if (col - 1) >= 0 and [row, col - 1] not in active_list:
                    neighbors.append({'position': [row, col - 1], 'cost': game_map[row][col - 1].cost(), 'side': 'w'})

                # neighbours collected -> sort them
                average(neighbors, active_list)
                neighbors.sort(key=cost_sort)

                for i in range(len(neighbors)):
                    # active_list.append(neighbors[i]['position'])
                    neighbors[i]['path'] = active_list.copy()
                    stack_of_neighbors.append(neighbors[i])

                new = stack_of_neighbors.pop(0)
                row = new['position'][0]
                col = new['position'][1]
                active_list = new['path']
                current = {'position': [row, col], 'path': active_list}

            else:
                active_list.append(current['position'])
                # path = current['path']
                break

        for i in range(1, len(active_list)):
            path.append(game_map[active_list[i][0]][active_list[i][1]])
        return path


class Draza(Agent):    # BBS
    def __init__(self, row, col, file_name):
        super().__init__(row, col, file_name)

    def get_agent_path(self, game_map, goal):
        path = [game_map[self.row][self.col]]

        def cost_sort(e):
            return e['cost']

        active_list = []
        neighbors = []
        equal_neighbors = []
        stack_of_neighbors = []

        row = self.row
        col = self.col
        current = {'position': [row, col], 'cost': 0, 'path': []}

        north = [-1, 0]
        east = [0, 1]
        south = [1, 0]
        west = [0, -1]

        max_row = len(game_map) - 1
        max_col = len(game_map[0]) - 1

        while True:
            north[0] = current['position'][0] - 1
            north[1] = current['position'][1]
            east[0] = current['position'][0]
            east[1] = current['position'][1] + 1
            south[0] = current['position'][0] + 1
            south[1] = current['position'][1]
            west[0] = current['position'][0]
            west[1] = current['position'][1] - 1

            active_list = current['path']

            # collecting neighbors
            if (current['position'][0] != goal[0] or current['position'][1] != goal[1]) and current['position'] not in active_list:
                active_list.append(current['position'])
                neighbors.clear()
                equal_neighbors.clear()
                # north
                if (row - 1) >= 0 and [row - 1, col] not in active_list:
                    neighbors.append({'position': [row - 1, col], 'cost': game_map[row - 1][col].cost(), 'side': 'n'})

                # east
                if (col + 1) <= max_col and [row, col + 1] not in active_list:
                    neighbors.append({'position': [row, col + 1], 'cost': game_map[row][col + 1].cost(), 'side': 'e'})

                # south
                if (row + 1) <= max_row and [row + 1, col] not in active_list:
                    neighbors.append({'position': [row + 1, col], 'cost': game_map[row + 1][col].cost(), 'side': 's'})

                # west
                if (col - 1) >= 0 and [row, col - 1] not in active_list:
                    neighbors.append({'position': [row, col - 1], 'cost': game_map[row][col - 1].cost(), 'side': 'w'})

                for i in range(len(neighbors)):
                    neighbors[i]['cost'] = neighbors[i]['cost'] + current['cost']
                    neighbors[i]['path'] = active_list.copy()
                    stack_of_neighbors.append(neighbors[i])

                stack_of_neighbors.sort(key=cost_sort)

                for i in range(1, len(stack_of_neighbors)):
                    first = stack_of_neighbors[0]
                    if stack_of_neighbors[i]['cost'] == first['cost'] and len(stack_of_neighbors[i]['path']) < len(first['path']):
                        first = stack_of_neighbors[i]
                        stack_of_neighbors[i] = stack_of_neighbors[0]
                        stack_of_neighbors[0] = first

                new = stack_of_neighbors.pop(0)
                cost = new['cost']
                row = new['position'][0]
                col = new['position'][1]
                active_list = new['path']
                current = {'position': [row, col],'cost': cost, 'path': active_list}

            else:
                active_list.append(current['position'])
                # path = current['path']
                break

        for i in range(1, len(active_list)):
            path.append(game_map[active_list[i][0]][active_list[i][1]])
        return path

class Bole(Agent):      # A*
    def __init__(self, row, col, file_name):
        super().__init__(row, col, file_name)

    def get_agent_path(self, game_map, goal):
        path = [game_map[self.row][self.col]]

        def cost_sort(e):
            return e['cost']

        def heuristic(c, n):
            for j in range(len(n)):
                new_cost = math.dist(c['position'], n[j]['position']) + n[j]['cost']
                n[j]['cost'] = new_cost


        active_list = []
        neighbors = []
        equal_neighbors = []
        stack_of_neighbors = []

        row = self.row
        col = self.col
        current = {'position': [row, col], 'cost': 0, 'path': []}

        north = [-1, 0]
        east = [0, 1]
        south = [1, 0]
        west = [0, -1]

        max_row = len(game_map) - 1
        max_col = len(game_map[0]) - 1

        while True:
            north[0] = current['position'][0] - 1
            north[1] = current['position'][1]
            east[0] = current['position'][0]
            east[1] = current['position'][1] + 1
            south[0] = current['position'][0] + 1
            south[1] = current['position'][1]
            west[0] = current['position'][0]
            west[1] = current['position'][1] - 1

            active_list = current['path']

            # collecting neighbors
            if (current['position'][0] != goal[0] or current['position'][1] != goal[1]) and current['position'] not in active_list:
                active_list.append(current['position'])
                neighbors.clear()
                equal_neighbors.clear()
                # north
                if (row - 1) >= 0 and [row - 1, col] not in active_list:
                    neighbors.append({'position': [row - 1, col], 'cost': game_map[row - 1][col].cost(), 'side': 'n'})

                # east
                if (col + 1) <= max_col and [row, col + 1] not in active_list:
                    neighbors.append({'position': [row, col + 1], 'cost': game_map[row][col + 1].cost(), 'side': 'e'})

                # south
                if (row + 1) <= max_row and [row + 1, col] not in active_list:
                    neighbors.append({'position': [row + 1, col], 'cost': game_map[row + 1][col].cost(), 'side': 's'})

                # west
                if (col - 1) >= 0 and [row, col - 1] not in active_list:
                    neighbors.append({'position': [row, col - 1], 'cost': game_map[row][col - 1].cost(), 'side': 'w'})

                for i in range(len(neighbors)):
                    neighbors[i]['cost'] = neighbors[i]['cost'] + current['cost']
                    neighbors[i]['path'] = active_list.copy()

                heuristic(current, neighbors)

                for i in range(len(neighbors)):
                    stack_of_neighbors.append(neighbors[i])

                stack_of_neighbors.sort(key=cost_sort)

                for i in range(1, len(stack_of_neighbors)):
                    first = stack_of_neighbors[0]
                    if stack_of_neighbors[i]['cost'] == first['cost'] and len(stack_of_neighbors[i]['path']) < len(first['path']):
                        first = stack_of_neighbors[i]
                        stack_of_neighbors[i] = stack_of_neighbors[0]
                        stack_of_neighbors[0] = first

                new = stack_of_neighbors.pop(0)
                cost = new['cost']
                row = new['position'][0]
                col = new['position'][1]
                active_list = new['path']
                current = {'position': [row, col],'cost': cost, 'path': active_list}

            else:
                active_list.append(current['position'])
                # path = current['path']
                break

        for i in range(1, len(active_list)):
            path.append(game_map[active_list[i][0]][active_list[i][1]])
        return path

class Tile(BaseSprite):
    def __init__(self, row, col, file_name):
        super(Tile, self).__init__(row, col, file_name)

    def position(self):
        return self.row, self.col

    def cost(self):
        pass

    def kind(self):
        pass


class Stone(Tile):
    def __init__(self, row, col):
        super().__init__(row, col, 'stone.png')

    def cost(self):
        return 1000

    def kind(self):
        return 's'


class Water(Tile):
    def __init__(self, row, col):
        super().__init__(row, col, 'water.png')

    def cost(self):
        return 500

    def kind(self):
        return 'w'


class Road(Tile):
    def __init__(self, row, col):
        super().__init__(row, col, 'road.png')

    def cost(self):
        return 2

    def kind(self):
        return 'r'


class Grass(Tile):
    def __init__(self, row, col):
        super().__init__(row, col, 'grass.png')

    def cost(self):
        return 3

    def kind(self):
        return 'g'


class Mud(Tile):
    def __init__(self, row, col):
        super().__init__(row, col, 'mud.png')

    def cost(self):
        return 5

    def kind(self):
        return 'm'


class Dune(Tile):
    def __init__(self, row, col):
        super().__init__(row, col, 'dune.png')

    def cost(self):
        return 7

    def kind(self):
        return 's'


class Goal(BaseSprite):
    def __init__(self, row, col):
        super().__init__(row, col, 'x.png', config.DARK_GREEN)


class Trail(BaseSprite):
    def __init__(self, row, col, num):
        super().__init__(row, col, 'trail.png', config.DARK_GREEN)
        self.num = num

    def draw(self, screen):
        text = config.GAME_FONT.render(f'{self.num}', True, config.WHITE)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)
