import encode


class WumpusWorld:
    def __init__(self):
        self.size = None
        self.world = []

    def load(self, file):
        raw_map = []

        with open(file, 'r') as f:
            # Read the size of the world
            self.size = int(f.readline())

            # Read the world
            for line in f:
                line = line[:-1].split('.')
                raw_map.append(line)

        for i in range(self.size):
            self.world.append([
                f'{raw_map[i][j]};'
                if raw_map[i][j] != '-'
                else ''
                for j in range(self.size)
            ])

        for i in range(self.size):
            for j in range(self.size):
                if self.world[i][j] == 'P;':
                    if i > 0:
                        self.world[i-1][j] += 'B;'
                    if i < self.size - 1:
                        self.world[i+1][j] += 'B;'
                    if j > 0:
                        self.world[i][j-1] += 'B;'
                    if j < self.size - 1:
                        self.world[i][j+1] += 'B;'
                elif self.world[i][j] == 'W;':
                    if i > 0:
                        self.world[i-1][j] += 'S;'
                    if i < self.size - 1:
                        self.world[i+1][j] += 'S;'
                    if j > 0:
                        self.world[i][j-1] += 'S;'
                    if j < self.size - 1:
                        self.world[i][j+1] += 'S;'

        self.world = [
            [cell[:-1].split(';') for cell in row]
            for row in self.world
        ]

        print(self.world)

        '''
        From this, use the encode_bits function to encode each state
        '''

        for i in range(self.size):
            for j in range(self.size):
                self.world[i][j] = encode.encode_bits(
                    1 if 'A' in self.world[i][j] else 0,
                    1 if 'W' in self.world[i][j] else 0,
                    1 if 'P' in self.world[i][j] else 0,
                    1 if 'G' in self.world[i][j] else 0,
                    1 if 'B' in self.world[i][j] else 0,
                    1 if 'S' in self.world[i][j] else 0
                )

        print(self.world)


if __name__ == '__main__':
    world = WumpusWorld()
    world.load('map/world.txt')
