import sys
from const import *
from copy import deepcopy
from heapq import heappush, heappop
from sat_solver import KnowledgeBase
from world import WumpusWorld, Cell, literal


class AgentBrain:
    def __init__(self, world: WumpusWorld, output_file, verbose=False):
        '''
        For the map
        '''
        self.wumpus_map = world
        self.size = len(world.world)
        self.verbose = verbose
        self.output_file = output_file
        self.LIMIT = 10

        '''
        For the knowledge base
        of the agent
        '''
        self.kb = KnowledgeBase()

        '''
        Other information
        about the agent
        '''
        self.cur_pos = self.wumpus_map.agent_pos
        self.score = 0
        self.actions = []
        self.cur_direction = Directions.RIGHT
        self.give_up = False
        self.goal = None

        self.path = []
        self.percepts = []

    def __quay_deu_quay_deu(self, new_direction: Directions):
        from_int = self.cur_direction.value
        to_int = new_direction.value

        clock_wise = 0
        c_from, c_to = from_int, to_int
        while c_from != c_to:
            c_from = (c_from + 1) % 4
            clock_wise += 1

        counter_clock_wise = 0
        c_from, c_to = from_int, to_int
        while c_from != c_to:
            c_from = (c_from - 1) % 4
            counter_clock_wise += 1

        if clock_wise < counter_clock_wise:
            return States.RIGHT, clock_wise

        return States.LEFT, counter_clock_wise

    def __get_direction(self, new_pos: Cell):
        cur_x, cur_y = self.cur_pos.x, self.cur_pos.y
        new_x, new_y = new_pos.x, new_pos.y

        if new_x == cur_x:
            if new_y > cur_y:
                return Directions.RIGHT
            return Directions.LEFT
        if new_x > cur_x:
            return Directions.DOWN
        return Directions.UP

    def __rotate(self, direction: Directions):
        action, times = self.__quay_deu_quay_deu(direction)
        for _ in range(times):
            self.__add_action(action, self.cur_pos)
        self.cur_direction = direction

    def __move_from_to(self, new_pos: Cell):
        '''
        Move 2 adjacent cells
        '''

        direction = self.__get_direction(new_pos)

        # Rotate the agent to the correct direction
        action, times = self.__quay_deu_quay_deu(direction)

        for _ in range(times):
            self.__add_action(action, self.cur_pos)

        # Move the agent forward
        self.__add_action(States.FORWARD, self.cur_pos)
        self.cur_direction = direction

    def __get_cell(self, x, y):
        return self.wumpus_map.world[x][y]

    def __get_neighbors(self, pos: Cell) -> list[Cell]:
        x, y = pos.x, pos.y
        # print('Getting neighbors of', x, y)
        neighbors = []

        for dx, dy in zip([0, 1, 0, -1], [1, 0, -1, 0]):
            new_x, new_y = x + dx, y + dy
            if 0 <= new_x < self.size and 0 <= new_y < self.size:
                neighbors.append(self.__get_cell(new_x, new_y))

        return neighbors

    def __add_percept(self, cell: Cell):
        # print('Percepting', cell.x, cell.y)

        neighbors = self.__get_neighbors(cell)

        if cell.is_breeze:
            self.kb.add_clause([literal(BREEZE, cell.x, cell.y, True)])

            '''
            Clause:
            B(x,y) => P(x+1,y) v P(x-1,y) v P(x,y+1) v P(x,y-1)
            or in CNF:
            -B(x,y) v P(x+1,y) v P(x-1,y) v P(x,y+1) v P(x,y-1)
            '''

            clause = [literal(BREEZE, cell.x, cell.y, False)]
            for neighbor in neighbors:
                clause.append(literal(PIT, neighbor.x, neighbor.y, True))

            self.kb.add_clause(clause)

            '''
            Clause:
            P(x+1,y) v P(x-1,y) v P(x,y+1) v P(x,y-1) => B(x,y)
            each clause in CNF:
            -P(x+1,y) v B(x,y)
            '''

            for neighbor in neighbors:
                clause = [literal(PIT, neighbor.x, neighbor.y, False),
                          literal(BREEZE, cell.x, cell.y, True)]
                self.kb.add_clause(clause)
        else:
            self.kb.add_clause([literal(BREEZE, cell.x, cell.y, False)])

        if cell.has_stench():
            self.kb.add_clause([literal(STENCH, cell.x, cell.y, True)])

            '''
            Clause:
            S(x,y) => W(x+1,y) v W(x-1,y) v W(x,y+1) v W(x,y-1)
            or in CNF:
            -S(x,y) v W(x+1,y) v W(x-1,y) v W(x,y+1) v W(x,y-1)
            '''

            clause = [literal(STENCH, cell.x, cell.y, False)]
            for neighbor in neighbors:
                clause.append(literal(WUMPUS, neighbor.x, neighbor.y, True))

            # print('Adding clause', clause)

            self.kb.add_clause(clause)

            '''
            Clause:
            W(x+1,y) v W(x-1,y) v W(x,y+1) v W(x,y-1) => S(x,y)
            each clause in CNF:
            -W(x+1,y) v S(x,y)
            '''

            for neighbor in neighbors:
                clause = [literal(WUMPUS, neighbor.x, neighbor.y, False),
                          literal(STENCH, cell.x, cell.y, True)]
                # print('Adding clause', clause)
                self.kb.add_clause(clause)
        else:
            self.kb.add_clause([literal(STENCH, cell.x, cell.y, False)])

        self.kb.add_clause([literal(PIT, cell.x, cell.y, cell.is_pit)])
        self.kb.add_clause([literal(WUMPUS, cell.x, cell.y, cell.is_wumpus)])

    def __add_action(self, action, pos):
        convert = self.wumpus_map.dl_to_tb(pos.x, pos.y)

        x, y = convert[0], convert[1]

        if self.verbose:
            print("ACTION\t", action, x, y)

        self.percepts.append((action, x, y))

        if self.output_file:
            self.output_file.write(f'{action} {x} {y}\n')

        if action == States.FORWARD:
            self.score -= 10
            if self.verbose:
                print("Score:", self.score)
            self.actions.append('FORWARD')
            self.path.append((x, y))

        elif action == States.LEFT:
            self.actions.append('LEFT')

        elif action == States.RIGHT:
            self.actions.append('RIGHT')

        elif action == States.CLIMB:
            self.score += 10
            if self.verbose:
                print("Score:", self.score)
            self.actions.append('CLIMB')
            self.path.append((x, y))

        elif action == States.GRAB:
            self.score += 1000
            if self.verbose:
                print("Score:", self.score)
            self.actions.append('GRAB')

        elif action == States.SHOOT:
            self.score -= 100
            if self.verbose:
                print("Score:", self.score)
            self.actions.append('SHOOT')

        elif action == States.KILLED_BY_WUMPUS:
            self.score -= 1000
            if self.verbose:
                print("Score:", self.score)
            self.actions.append('KILLED_BY_WUMPUS')

        elif action == States.FALL_INTO_PIT:
            self.score -= 1000
            if self.verbose:
                print("Score:", self.score)
            self.actions.append('FALL_INTO_PIT')

    # A* for exiting the map
    def __manhattan_distance(self, pos1, pos2):
        return abs(pos1.x - pos2.x) + abs(pos1.y - pos2.y)

    def __a_star(self, start, goal):
        frontier = []
        heappush(frontier, (0, (start.x, start.y)))

        came_from = {}
        cost_so_far = {}

        came_from[(start.x, start.y)] = None
        cost_so_far[(start.x, start.y)] = 0

        while frontier:
            _, current = heappop(frontier)

            if current == (goal.x, goal.y):
                break

            for next in self.__get_neighbors(self.__get_cell(*current)):
                new_cost = cost_so_far[current] + 1
                if (next.x, next.y) not in cost_so_far or new_cost < cost_so_far[(next.x, next.y)]:
                    cost_so_far[(next.x, next.y)] = new_cost
                    priority = new_cost + self.__manhattan_distance(goal, next)
                    heappush(frontier, (priority, (next.x, next.y)))
                    came_from[(next.x, next.y)] = current

        path = []

        current = (goal.x, goal.y)
        while current != (start.x, start.y):
            path.append(current)
            current = came_from[current]

        path.reverse()

        start = self.wumpus_map.world[start.x][start.y]
        for x, y in path:
            next = self.wumpus_map.world[x][y]
            self.__move_from_to(next)
            self.cur_pos = next

    def backtrack(self):
        cell = self.cur_pos

        if self.wumpus_map.is_goal(cell.x, cell.y):
            self.__add_action(States.FIND_GOAL, cell)
            self.goal = cell

        if cell.is_wumpus:
            self.__add_action(States.KILLED_BY_WUMPUS, cell)
            if self.verbose:
                print('KILLED BY WUMPUS')
            return False

        if cell.is_pit:
            self.__add_action(States.FALL_INTO_PIT, cell)
            if self.verbose:
                print('FALL INTO PIT')
            return False

        if cell.is_gold:
            self.__add_action(States.GRAB, cell)
            if self.verbose:
                print('GOT GOLD')
            cell.grab_gold()

        if cell.is_breeze:
            self.__add_action(States.PERCEPT_PIT, cell)

        if cell.has_stench():
            self.__add_action(States.PERCEPT_WUMPUS, cell)

        if not cell.is_explored:
            self.__add_percept(cell)
            cell.is_explored = True

        # Remove the neighbors that is the parent of the current cell
        neighbors = [neighbor for neighbor in
                     self.__get_neighbors(cell)
                     if neighbor != cell.parent]

        # Store this call for later save parent
        tmp_parent = cell

        tmp_neighbors = []

        if not cell.is_safe():
            # Get all the non-pit neighbors
            neighbors = [n for n in neighbors
                         if not n.is_explored and not n.is_pit]

            tmp_neighbors = []

            if cell.has_stench():
                for n in neighbors:
                    if self.kb.infer(literal(WUMPUS, n.x, n.y, False)):
                        self.__rotate(self.__get_direction(n))

                        self.__add_action(States.DETECTED_WUMPUS, cell)
                        self.__add_action(States.SHOOT, cell)
                        self.__add_action(
                            States.PERCEPT_WUMPUS_KILLED, cell)

                        self.wumpus_map.kill_wumpus(n.x, n.y)

                        if not cell.has_stench():
                            '''
                            S -> W v W v W v W
                            '''

                            clause = [literal(STENCH, cell.x, cell.y, False)]

                            for neighbor in self.__get_neighbors(cell):
                                clause.append(
                                    literal(WUMPUS, neighbor.x, neighbor.y, True))

                            self.kb.remove_clause(clause)

                            self.kb.remove_clause([
                                literal(STENCH, cell.x, cell.y, True)
                            ])

                            self.kb.add_clause([
                                literal(STENCH, cell.x, cell.y, False)
                            ])
                    else:
                        if self.kb.infer(literal(WUMPUS, n.x, n.y, True)):
                            self.__add_action(States.PERCEPT_NO_WUMPUS, cell)
                        else:
                            tmp_neighbors.append(n)

            if cell.has_stench():
                '''
                Kill all
                '''

                adj_list = [
                    n for n in self.__get_neighbors(cell)
                    if not n.is_explored
                    and n != cell.parent
                ]

                for n in adj_list:
                    self.__rotate(self.__get_direction(n))

                    self.__add_action(States.SHOOT, cell)

                    if n.is_wumpus:
                        self.__add_action(
                            States.PERCEPT_WUMPUS_KILLED, cell)
                        self.wumpus_map.kill_wumpus(n.x, n.y)

                        if n.parent is None:
                            n.parent = cell
                            cell.children.append(n)

                    if not cell.has_stench():
                        clause = [literal(STENCH, cell.x, cell.y, False)]

                        for neighbor in self.__get_neighbors(cell):
                            clause.append(
                                literal(WUMPUS, neighbor.x, neighbor.y, True))

                        self.kb.remove_clause(clause)

                        self.kb.remove_clause([
                            literal(STENCH, cell.x, cell.y, True)
                        ])

                        self.kb.add_clause([
                            literal(STENCH, cell.x, cell.y, False)
                        ])

                        break

            if cell.is_breeze:
                for neighbor in neighbors:
                    self.__rotate(self.__get_direction(neighbor))
                    if self.kb.infer(literal(PIT, neighbor.x, neighbor.y, False)):
                        self.__add_action(States.DETECTED_PIT, cell)
                        self.__add_percept(neighbor)

                        neighbor.is_explored = True
                        neighbor.parent = neighbor.parent

                        tmp_neighbors.append(neighbor)
                    elif self.kb.infer(literal(PIT, neighbor.x, neighbor.y, True)):
                        self.__add_action(States.PERCEPT_NO_PIT, cell)
                    else:
                        tmp_neighbors.append(neighbor)

        tmp_neighbors = list(set(tmp_neighbors))
        for u in tmp_neighbors:
            neighbors.remove(u)

        for n in neighbors:
            if n.parent is None:
                n.parent = cell
                cell.children.append(n)

        neighbors = cell.children
        unvisited_neighbors = [n for n in neighbors if n.is_explored == False]
        visited_neighbors = [n for n in neighbors if n.is_explored == True]

        neighbors = unvisited_neighbors + visited_neighbors
        for adj in neighbors:
            self.__move_from_to(adj)
            self.cur_pos = adj

            if not self.backtrack():
                return False

            self.__move_from_to(tmp_parent)
            self.cur_pos = tmp_parent

        return True

    def solve(self):
        '''
        Backtracking the whole map
        and then A* to the exit
        '''
        if not self.backtrack():
            print('Cannot backtrack')
            return False

        if not self.goal:
            print('Cannot find goal')
            return False

        self.__a_star(self.cur_pos, self.goal)
        self.__add_action(States.CLIMB, self.goal)

        print('Path:', self.path)
        print('Score:', self.score)
