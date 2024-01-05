from copy import deepcopy

from const import Directions

def literal(type, x, y, pos):
    if not pos:
        return f'-{type}({x},{y})'
    else:
        return f'{type}({x},{y})'


class Cell:
    def __init__(self):
        self.x, self.y = None, None
        self.is_wumpus = False
        self.is_pit = False
        self.is_gold = False
        self.is_breeze = False

        self.num_stenches = 0

        self.is_explored = False
        self.parent = None
        self.children = []

    def is_safe(self):
        return not (self.has_stench() or self.is_breeze)

    def has_stench(self):
        return self.num_stenches > 0

    def kill_wumpus(self):
        self.is_wumpus = False

    def update_stench(self):
        self.num_stenches -= 1

    def grab_gold(self):
        self.is_gold = False


class WumpusWorld:
    def __init__(self):
        self.__size = None
        self.world = []
        self.agent_pos = None

        '''
        For graphic
        '''
        self.init_map = None

    def draw_map(self, direcion, x, y):
        game_map = [['' for _ in range(self.__size)] for _ in range(self.__size)]

        for i in range(self.__size):
            for j in range(self.__size):
                info = ''
                if i == x and j == y:
                    if direcion == Directions.RIGHT:
                        info += '>'
                    elif direcion == Directions.LEFT:
                        info += '<'
                    elif direcion == Directions.UP:
                        info += '^'
                    elif direcion == Directions.DOWN:
                        info += 'v'
                
                if self.world[i][j].is_wumpus:
                    info += 'W'
                
                if self.world[i][j].is_pit:
                    info += 'P'
                
                if self.world[i][j].is_gold:
                    info += 'G'
                
                if self.world[i][j].is_breeze:
                    info += 'B'
                
                if self.world[i][j].has_stench():
                    info += 'S'
                
                if self.world[i][j].is_explored:
                    info += 'E'
                
                if info == '':
                    info = '-'
                
                game_map[i][j] = info
    
        to_str = ''

        for row in game_map:
            to_str += ''.join(s.center(5) for s in row) + '\n'
        
        return to_str

    def dl_to_tb(self, i, j):
        return self.__size - i, j + 1

    def kill_wumpus(self, i, j):
        self.world[i][j].kill_wumpus()

        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            x, y = i + dx, j + dy
            if x in range(self.__size) and y in range(self.__size):
                self.world[x][y].update_stench()

    def load(self, file):
        raw_map = []

        with open(file, 'r') as f:

            self.__size = int(f.readline())

            for i in range(self.__size):
                self.world.append([Cell() for _ in range(self.__size)])

            for line in f:
                line = line[:-1].split('.')

                if len(line) != self.__size:
                    raise Exception('Invalid map')

                raw_map.append(line)

        for i in range(self.__size):
            for j in range(self.__size):
                self.world[i][j].x = i
                self.world[i][j].y = j

                data = raw_map[i][j]

                for char in data:
                    if char == 'A':
                        self.world[i][j].is_agent = True
                        self.agent_pos = self.world[i][j]
                        self.world[i][j].parent = self.world[i][j]
                    elif char == 'W':
                        self.world[i][j].is_wumpus = True
                        self.__set_stench(i, j)
                    elif char == 'P':
                        self.world[i][j].is_pit = True
                        self.__set_breeze(i, j)
                    elif char == 'G':
                        self.world[i][j].is_gold = True
                    elif char == '-':
                        pass
                    else:
                        raise Exception('Invalid character in map')
        
        self.init_map = deepcopy(self.world)

    def is_goal(self, i, j):
        return i == self.__size - 1 and j == 0

    def __set_breeze(self, i, j):
        if i > 0:
            self.world[i-1][j].is_breeze = True
        if i < self.__size - 1:
            self.world[i+1][j].is_breeze = True
        if j > 0:
            self.world[i][j-1].is_breeze = True
        if j < self.__size - 1:
            self.world[i][j+1].is_breeze = True

    def __set_stench(self, i, j):
        if i > 0:
            self.world[i-1][j].num_stenches += 1
        if i < self.__size - 1:
            self.world[i+1][j].num_stenches += 1
        if j > 0:
            self.world[i][j-1].num_stenches += 1
        if j < self.__size - 1:
            self.world[i][j+1].num_stenches += 1

    def remove_stench(self, i, j):
        if i > 0:
            self.world[i-1][j].num_stenches -= 1
        if i < self.__size - 1:
            self.world[i+1][j].num_stenches -= 1
        if j > 0:
            self.world[i][j-1].num_stenches -= 1
        if j < self.__size - 1:
            self.world[i][j+1].num_stenches -= 1
