# Python
import pygame
import sys
import time

# Game settings
FPS = 60
CELL_SIZE = 40
WIDTH, HEIGHT = CELL_SIZE * 10, CELL_SIZE * 10

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GOLD = (255, 223, 0)
# Initialize Pygame
pygame.init()
font = pygame.font.Font(None, 36)

player_direction = '>'  # Initial direction is upward


player_surface = pygame.Surface((CELL_SIZE, CELL_SIZE))
player_surface.fill(RED)


# Initialize the window
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Wumpus World")

# Initialize game variables
cave_size = 10
player_position = [0, 0]
visited_cells = [list(player_position)]
wumpus_positions = [[2, 2], [4, 4]]
pit_positions = [[1, 1], [3, 3]]
breeze_positions = [[x+dx, y+dy] for x, y in pit_positions for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)] if 0 <= x+dx < cave_size and 0 <= y+dy < cave_size]
stench_positions = [[x+dx, y+dy] for x, y in wumpus_positions for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)] if 0 <= x+dx < cave_size and 0 <= y+dy < cave_size]
arrow = 10
wumpus_alives = [True for _ in wumpus_positions]
move_delay = 0.2  # Delay between each move in seconds
last_move_time = time.time()
gold_positions= [[4, 4], [5, 4]]
gold_captured = False
shoot_wumpus = None
won=False

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                if player_direction == '^':
                    player_direction = '<'
                elif player_direction == 'v':
                    player_direction = '>'
                elif player_direction == '<':
                    player_direction = 'v'
                elif player_direction == '>':
                    player_direction = '^'
            elif event.key == pygame.K_RIGHT:
                if player_direction == '^':
                    player_direction = '>'
                elif player_direction == 'v':
                    player_direction = '<'
                elif player_direction == '<':
                    player_direction = '^'
                elif player_direction == '>':
                    player_direction = 'v'
            elif event.key == pygame.K_UP:
                if player_direction == '^' and player_position==[0,0]:
                    print("Win")
                    won=True
                    break
                if player_direction == '^' and player_position[1] > 0:
                    player_position[1] -= 1
                elif player_direction == 'v' and player_position[1] < cave_size - 1:
                    player_position[1] += 1
                elif player_direction == '<' and player_position[0] > 0:
                    player_position[0] -= 1
                elif player_direction == '>' and player_position[0] < cave_size - 1:
                    player_position[0] += 1
            elif event.key == pygame.K_DOWN:
                if player_direction == '^' and player_position[1] < cave_size - 1:
                    player_direction = 'v'
                    player_position[1] += 1
                elif player_direction == 'v' and player_position[1] > 0:
                    player_direction = '^'
                    player_position[1] -= 1
                elif player_direction == '<' and player_position[0] < cave_size - 1:
                    player_direction = '>'
                    player_position[0] += 1
                elif player_direction == '>' and player_position[0] > 0:
                    player_direction = '<'
                    player_position[0] -= 1
            elif event.key == pygame.K_SPACE:
                    print(f"Space key pressed. Arrows left: {arrow}")
                    if arrow:
                        print("You shot an arrow!")
                        if event.key == pygame.K_SPACE:
                            print(f"Space key pressed. Arrows left: {arrow}")
                            if arrow:
                                print("You shot an arrow!")
                                if ((player_direction == '^' and [player_position[0], player_position[1]-1] in wumpus_positions) or
                                    (player_direction == 'v' and [player_position[0], player_position[1]+1] in wumpus_positions) or
                                    (player_direction == '<' and [player_position[0]-1, player_position[1]] in wumpus_positions) or
                                    (player_direction == '>' and [player_position[0]+1, player_position[1]] in wumpus_positions)):
                                    if player_direction == '^':
                                        wumpus_alives[wumpus_positions.index([player_position[0], player_position[1]-1])] = False 
                                        shoot_wumpus = [player_position[0], player_position[1]-1]
                                        print(shoot_wumpus)
                                    elif player_direction == 'v':
                                        wumpus_alives[wumpus_positions.index([player_position[0], player_position[1]+1])] = False
                                        shoot_wumpus = [player_position[0], player_position[1]+1]
                                    elif player_direction == '<':
                                        wumpus_alives[wumpus_positions.index([player_position[0]-1, player_position[1]])] = False
                                        shoot_wumpus = [player_position[0]-1, player_position[1]]
                                    elif player_direction == '>':
                                        wumpus_alives[wumpus_positions.index([player_position[0]+1, player_position[1]])] = False 
                                        shoot_wumpus = [player_position[0]+1, player_position[1]]    
                                    

                                arrow -= 1

            elif event.key == pygame.K_RETURN:
                if player_position in gold_positions:
                    gold_captured = True
    if won:
        break
    # Update visited cells
    if list(player_position) not in visited_cells:
        visited_cells.append(list(player_position))

    # Update game state
    if player_position in pit_positions:
        print("You fell into a pit!")
        break
    elif player_position in wumpus_positions and wumpus_alives[wumpus_positions.index(player_position)]:
        print("You were eaten by the wumpus!")
        break
    elif shoot_wumpus is not None and shoot_wumpus in wumpus_positions and not wumpus_alives[wumpus_positions.index(shoot_wumpus)] :
        print("You killed the wumpus!")
        wumpus_positions.remove(shoot_wumpus)
        stench_positions = [[x+dx, y+dy] for x, y in wumpus_positions for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)] if 0 <= x+dx < cave_size and 0 <= y+dy < cave_size]
        shoot_wumpus = None
        
    
    if gold_captured:
        print("You captured the gold!")
        gold_captured = False
        

    if player_position in breeze_positions or player_position in stench_positions:
        player_surface.set_alpha(128)  # Semi-transparent
    else:
        player_surface.set_alpha(255)  # Opaque

    

    # Draw game state
    count=0
    win.fill(BLACK)
    for cell in visited_cells:
        
                 

        if cell in gold_positions and cell in stench_positions:
            # Render 's' text
            text = font.render('s', True, (0, 0, 0))

            # Draw cell with gold background
            pygame.draw.rect(win, GOLD, (cell[0]*CELL_SIZE, cell[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE))

            # Blit the text onto the window at the cell's position
            win.blit(text, (cell[0]*CELL_SIZE, cell[1]*CELL_SIZE))
        elif cell in gold_positions:
            pygame.draw.rect(win, GOLD, (cell[0]*CELL_SIZE, cell[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE))
        else:
            pygame.draw.rect(win, WHITE, (cell[0]*CELL_SIZE, cell[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE))
        if cell in breeze_positions and cell in stench_positions:
            text = font.render('bs', True, (0, 0, 255))
            win.blit(text, (cell[0]*CELL_SIZE, cell[1]*CELL_SIZE))
        elif cell in breeze_positions:
            text = font.render('b', True, (0, 0, 255))
            win.blit(text, (cell[0]*CELL_SIZE, cell[1]*CELL_SIZE))
        elif cell in stench_positions:
            text = font.render('s', True, (0, 0, 0))
            win.blit(text, (cell[0]*CELL_SIZE, cell[1]*CELL_SIZE))
    
    
    text = font.render(player_direction, True, RED)
    text_rect = text.get_rect(center=(player_position[0]*CELL_SIZE + CELL_SIZE//2, player_position[1]*CELL_SIZE + CELL_SIZE//2))
    win.blit(text, text_rect)
    pygame.display.flip()


    pygame.time.Clock().tick(FPS)