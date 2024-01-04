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

    # def is_safe(self):
    #     return not self.__is_wumpus and not self.__is_pit

    # def has_stench(self):
    #     return self.num_stenches > 0

    # def is_wumpus(self):
    #     return self.__is_wumpus

    # def is_pit(self):
    #     return self.__is_pit

    # def is_gold(self):
    #     return self.__is_gold

    def grab_gold(self):
        self.is_gold = False

    # def is_breeze(self):
    #     return self.__is_breeze

    # def kill_wumpus(self):
    #     self.__is_wumpus = False

    # def update_stench(self):
    #     self.num_stenches -= 1


class WumpusWorld:
    def __init__(self):
        self.__size = None
        self.world = []
        self.agent_pos = None

    def kill_wumpus(self, i, j):
        self.world[i][j].kill_wumpus()

        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            x, y = i + dx, j + dy
            if 0 <= x < self.__size and 0 <= y < self.__size:
                self.world[x][y].update_stench()

    def load(self, file):
        raw_map = []

        with open(file, 'r') as f:
            # Read the size of the world
            self.__size = int(f.readline())

            for i in range(self.__size):
                self.world.append([Cell() for _ in range(self.__size)])

            # Read the world
            for line in f:
                line = line[:-1].split('.')
                raw_map.append(line)

        for i in range(self.__size):
            for j in range(self.__size):
                self.world[i][j].x = i
                self.world[i][j].y = j

                if raw_map[i][j] == 'A':
                    # print('Agent at', i, j)
                    self.world[i][j].is_agent = True
                    self.agent_pos = self.world[i][j]
                elif raw_map[i][j] == 'W':
                    self.world[i][j].is_wumpus = True
                    self.__set_stench(i, j)
                elif raw_map[i][j] == 'P':
                    self.world[i][j].is_pit = True
                    self.__set_breeze(i, j)
                elif raw_map[i][j] == 'G':
                    self.world[i][j].is_gold = True

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
