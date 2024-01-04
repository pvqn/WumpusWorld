import functools
from queue import Queue
from FileIO import read_file

# Constant value
G, S, W, B, P = 0, 1, 2, 3, 4
RIGHT, DOWN, LEFT, UP = 0, 1, 2, 3

file_path = 'hta.txt'
map_size, map_layout = None, None
agent_position, map_state, percept_state = None, None, None
direction = 0               # Right: 0      Up: 1       Left: 2     Down: 3
total_score = 0
frontier = []

# Explain for percept_state: ( visited, stench, wumpus, breeze, pit )
# visited   :   [ 0, 1 ]    -> not visited | visited
# stench    :   [ 0, 4 ]    -> number of hidden wumpus around ( maybe )     
# wumpus    :   [ 0, 4 ]    -> number of hints for being wumpus             5: absolutely yes
# breeze    :   [ 0, 4 ]    -> number of hidden pits around ( maybe )
# pit       :   [ 0, 4 ]    -> number of hints for being pit                5: absolutely yes

# ========================================================= Support function ================================================================
def CheckValid( current_position ):
    
    if( ( 0 <= current_position[0] < map_size ) and ( 0 <= current_position[1] < map_size ) ): return True
    else: return False

def CheckState( current_position, key ):
    
    current_x, current_y = current_position
    if( ( map_state[current_x][current_y] & ( 1 << key ) ) != 0 ): return True 
    else: return False

def GetNeighbor( current_position ):

    neighbor = []
    
    moveX = [0, 1, 0, -1]
    moveY = [1, 0, -1, 0]

    current_x, current_y = current_position

    for _ in range(4):
        _x = current_x + moveX[_]
        _y = current_y + moveY[_]

        if( not CheckValid( ( _x, _y ) ) ): continue

        neighbor.append( ( _x, _y ) )
    
    return neighbor

def ManhattanDistance( position_A, position_B ):
    return abs( position_A[0] - position_B[0] ) + abs( position_A[1] - position_B[1] )

def CheckSaved( current_position ):
    if( percept_state[current_position[0]][current_position[1]][W] == 0 and percept_state[current_position[0]][current_position[1]][P] == 0 ): return True 
    else: return False

def CustomSort( A, B ):

    if ( percept_state[A[0]][A[1]][P] > 0 and percept_state[A[0]][A[1]][W] in [None, 0] ) and ( percept_state[B[0]][B[1]][P] and percept_state[B[0]][B[1]][W] in [None, 0] ) > 0:
        if percept_state[A[0]][A[1]][P] < percept_state[B[0]][B[1]][P]: return -1
        elif percept_state[A[0]][A[1]][P] > percept_state[B[0]][B[1]][P]: return 1
        elif ManhattanDistance(A, agent_position) != ManhattanDistance(B, agent_position):
            return -1 if ManhattanDistance(A, agent_position) < ManhattanDistance(B, agent_position) else 1
    
    if( percept_state[A[0]][A[1]][P] > 0 ): return 1
    if( percept_state[B[0]][B[1]][P] > 0 ): return -1

    if( not CheckSaved(A) or not CheckSaved(B) ):
        if( not CheckSaved(B) ): return -1
        else: return 1

    if( ManhattanDistance( A, agent_position ) != ManhattanDistance( B, agent_position ) ):
        if( ManhattanDistance( A, agent_position ) < ManhattanDistance( B, agent_position ) ): return -1
        else: return 1

    A = percept_state[A[0]][A[1]]
    B = percept_state[B[0]][B[1]]
    
    if( A[W] != B[W] and A[W] > 0 and B[W] > 0 ):
        if( A[W] > B[W] ): return - 1
        else: return 1
    
    return 0
# =======================================================================

def UpdatePercept( current_position, index, value ):
    
    global percept_state

    v, s, w, b, p = percept_state[current_position[0]][current_position[1]]
    value = min( value, 5 )
    
    if( index == 0 ): v = value
    if( index == 1 ): s = value
    if( index == 2 ): w = value
    if( index == 3 ): b = value
    if( index == 4 ): p = value

    percept_state[current_position[0]][current_position[1]] = ( v, s, w, b, p )

def UpdateDanger( current_position, index ):
    global percept_state

    if( index not in [W, P] ): return
    current_x, current_y = current_position

    if( percept_state[current_x][current_y][0] == 1 ): return
    if( percept_state[current_x][current_y][index] in [0, 5] ): return

    updateValue = 0
    for _x, _y in GetNeighbor( current_position ):

        if( percept_state[_x][_y][0] == 0 ): continue
        if( percept_state[_x][_y][index - 1] == 0 ):
            updateValue = -1
            break
        updateValue += 1
    
    if( updateValue == 0 ): updateValue = None
    if( updateValue == -1 ): updateValue = 0
    
    if( index == W ): percept_state[current_x][current_y] = ( percept_state[current_x][current_y][0], percept_state[current_x][current_y][S], updateValue, percept_state[current_x][current_y][B], percept_state[current_x][current_y][P] )
    if( index == P ): percept_state[current_x][current_y] = ( percept_state[current_x][current_y][0], percept_state[current_x][current_y][S], percept_state[current_x][current_y][W], percept_state[current_x][current_y][B], updateValue )

def UpdateHint( current_position, index ):
    global percept_state

    current_x, current_y = current_position

    if( index not in [S, B] ): return

    if( percept_state[current_x][current_y][0] == 0 ): return
    if( percept_state[current_x][current_y][index] in [ None, 0 ] ): return

    updateValue = 0
    for _x, _y in GetNeighbor( current_position ):

        if( percept_state[_x][_y][0] == 1 ): continue

        if( percept_state[_x][_y][index + 1] == 0 ): continue

        updateValue += 1
    
    if( index == S ): percept_state[current_x][current_y] = ( percept_state[current_x][current_y][0], updateValue, percept_state[current_x][current_y][W], percept_state[current_x][current_y][B], percept_state[current_x][current_y][P] )
    if( index == B ): percept_state[current_x][current_y] = ( percept_state[current_x][current_y][0], percept_state[current_x][current_y][S], percept_state[current_x][current_y][W], updateValue, percept_state[current_x][current_y][P] )

def UpdateSmell( current_position ):
    global map_state

    for position in GetNeighbor( current_position ):
        if( CheckState( position, S ) ): map_state[position[0]][position[1]] ^= ( 1 << S )
        for _ in GetNeighbor( position ):
            if( CheckState( _, W ) ):
                map_state[position[0]][position[1]] ^= ( 1 << S )
                break

# ===================================================
    
def EntailDanger( current_position ):

    global frontier

    current_x, current_y = current_position

    if( percept_state[current_x][current_y][S] == 1 ):
        for _x, _y in GetNeighbor( current_position ): 
            if( percept_state[_x][_y][W] != 0 ): 
                UpdatePercept( ( _x, _y ), W, 5 )
                UpdatePercept( ( _x, _y ), P, 0 )
    
    if( percept_state[current_x][current_y][B] == 1 ):
        for _x, _y in GetNeighbor( current_position ): 
            if( percept_state[_x][_y][P] != 0 ): 
                UpdatePercept( ( _x, _y ), W, 0 )
                UpdatePercept( ( _x, _y ), P, 5 )

                frontier.remove( ( _x, _y ) )

def NotKillThisWumpus( current_position ):

    current_x, current_y = current_position
    if( percept_state[current_x][current_y][W] in [0, None] ): return False
    if( len(GetNeighbor( current_position )) < 4 ): return False

    for _x, _y in GetNeighbor( current_position ):
        if( percept_state[_x][_y][0] == 0 and ( percept_state[_x][_y][P] not in [0, 5] or percept_state[_x][_y][W] not in [0, 5] ) ): return True
    
    return False
                

# ========================================================== Action function ================================================================

def FindPath( Goal ):

    expanded = Queue()
    visited = dict()

    expanded.put( Goal )
    visited[Goal] = 0

    while( not expanded.empty() ):
        current_position = expanded.get()

        for node in GetNeighbor( current_position ):
            if( percept_state[node[0]][node[1]][0] == 0 ): continue
            if( node in visited ): continue
            visited[node] = visited[current_position] + 1
            expanded.put(node)
    
    path = []
    current = agent_position
    while( visited[current] != 0 ):
        path.append( current )
        for node in GetNeighbor( current ):
            if( node not in visited ): continue
            if( visited[node] == visited[current] - 1 ):
                current = node
                break
    # print( Goal, path )
    path.remove( agent_position )

    return path

def MoveOneStep( position ):
    global agent_position, total_score

    if( position == agent_position ): return
    total_score -= 10

    agent_position = position
    CollectGold( agent_position )
    ReceivePercept( agent_position )

    print( 'ACTION   States.FORWARD ', agent_position[0], agent_position[1] )
    print( 'Score: ', total_score )

def ShotArrow( position ):
    global map_state, percept_state, total_score

    UpdatePercept( position, W, 0 )
    total_score -= 100

    print('ACTION   States.SHOT ', agent_position[0], agent_position[1])
    print('Score: ', total_score)

    if( CheckState( position, W ) ): 
        map_state[position[0]][position[1]] ^= ( 1 << W )
        UpdateSmell( position )
        print('Wumpus screammmmmmmmm')
        return True
    
    return False

def CollectGold( position ):
    global map_state, total_score

    if( CheckState( position, G ) ):
        map_state[position[0]][position[1]] ^= ( 1 << G )
        total_score += 1000
        print('ACTION   States.COLLECT ', agent_position[0], agent_position[1])
        print('Score: ', total_score )

def TurnAround( position, goal_position ):

    global direction
    direct_map = [ ( 0, 1 ), ( -1, 0 ), ( 0, -1 ), ( 1, 0 ) ]
    direct = ( goal_position[0] - position[0], goal_position[1] - position[1] )

    if( direct == ( 0, 0 ) ): return

    if( direct == direct_map[direction] ): return
    if( direct == direct_map[(direction + 1) % 4] ):
        direction = (direction + 1) % 4
        print('ACTION   States.LEFT ', agent_position[0], agent_position[1])
        return
    if( direct == direct_map[(direction + 3) % 4] ):
        direction = (direction + 3) % 4
        print('ACTION   States.RIGHT ', agent_position[0], agent_position[1])
        return
    
    direction = ( direction + 2 ) % 4
    print('ACTION   States.RIGHT ', agent_position[0], agent_position[1])
    print('ACTION   States.RIGHT ', agent_position[0], agent_position[1])
    return


def FindNextGoal():

    global frontier, agent_position

    for position in frontier:
        if( NotKillThisWumpus( position ) ): frontier.remove( position )

    frontier = sorted( frontier, key =  functools.cmp_to_key(CustomSort) )
    # Get the next goal
    Goal = frontier[0]
    # Go to that goal
    path = FindPath( Goal )
    for step in path: 
        TurnAround( agent_position, step )
        MoveOneStep( step )

    TurnAround( agent_position, Goal )

    if( percept_state[Goal[0]][Goal[1]][W] > 0 ): 
        if ( ShotArrow( Goal ) ):
            ReceivePercept( agent_position )
            agent_position = Goal 
            ReceivePercept( agent_position )
            frontier.remove(Goal)
        return
    
    MoveOneStep( Goal )
    frontier.remove(Goal)

def Solver():

    global agent_position, frontier

    PreProcess()
    frontier = sorted( frontier, key =  functools.cmp_to_key(CustomSort) )
    CollectGold( agent_position )

    while( len( frontier ) > 0 ):
        FindNextGoal()
        if( len( frontier ) > 0 and percept_state[map_size - 1][0][0] == 1 and percept_state[frontier[0][0]][frontier[0][1]][W] in [None, 0] and percept_state[frontier[0][0]][frontier[0][1]][P] not in [None, 0] ): break
    if( percept_state[map_size - 1][0][0] == 0 ): EndGame()

    path = FindPath( ( map_size - 1, 0 ) )
    for step in path: 
        TurnAround( agent_position, step )
        MoveOneStep( step )
    
    TurnAround( agent_position, ( map_size - 1, 0 ) )
    
    if( percept_state[map_size - 1][0][W] > 0 ): 
        ShotArrow( ( map_size - 1, 0 ) )
        ReceivePercept( agent_position )
    MoveOneStep( ( map_size - 1, 0 ) )

    Win()

# ============================================================= End Game ====================================================================
def EndGame():
    print( "You die")
    exit()

def Win():
    global total_score

    total_score += 10

    print( 'Exit dungeon' )
    print( 'Total score: ', total_score )
    exit()
# ===========================================================================================================================================

def PreProcess() :
    global map_size, map_layout
    global agent_position, map_state, percept_state

    # Read map from file
    map_size, map_layout = read_file(file_path)

    # Initialization
    map_state = [[0] * map_size for _ in range(map_size)]
    percept_state = [[( 0, None, None, None, None )] * map_size for _ in range(map_size)]

    # Process
    for _ in range(map_size):
        for __ in range(map_size):
            if( 'A' in map_layout[_][__]  ): 
                agent_position = ( _, __ )
                map_layout[_][__].replace( 'A', '')

    for _ in range(map_size):
        for __ in range(map_size):
            if( 'W' in map_layout[_][__] ):
                map_state[_][__] |= ( 1 << W )
                for _x, _y in GetNeighbor( ( _, __ ) ): map_state[_x][_y] |= ( 1 << S )
            if( 'P' in map_layout[_][__] ):
                map_state[_][__] |= ( 1 << P )
                for _x, _y in GetNeighbor( ( _, __ ) ): map_state[_x][_y] |= ( 1 << B )
            if( 'G' in map_layout[_][__] ): map_state[_][__] |= ( 1 << G )
    
    # Start percept
    CollectGold( agent_position )
    ReceivePercept( agent_position )

def ReceivePercept( current_position ):

    global percept_state, frontier

    current_x, current_y = current_position
    
    visited, stench, wumpus, breeze, pit = percept_state[current_x][current_y]

    # print( current_position )

    # :333333333333333333333333333 End game :33333333333333333333333333333
    if( CheckState( current_position, W ) or CheckState( current_position, P ) ): EndGame()

    # Mark as visited
    visited = 1
    stench, wumpus, breeze, pit = 0, 0, 0, 0

    # Add frontier
    for _x, _y in GetNeighbor( current_position ):
        
        if( percept_state[_x][_y][0] == 1 ): continue
        if( ( _x, _y ) in frontier ): continue

        frontier.append( ( _x, _y ) )

    # If current position do not have any hint
    if( not ( CheckState( current_position, S ) or CheckState( current_position, B ) ) ):

        for position in GetNeighbor( current_position ):

            UpdatePercept( position, W, 0 )
            UpdatePercept( position, P, 0 )
        
        percept_state[current_x][current_y] = ( visited, stench, wumpus, breeze, pit )

        for position in GetNeighbor( current_position ):
            UpdateHint( position, S )
            UpdateHint( position, B )

        return

    # Current position is stench
    if( CheckState( current_position, S ) ):

        for _x, _y in GetNeighbor( current_position ):

            if( percept_state[_x][_y][0] == 1 ): continue
            if( percept_state[_x][_y][W] == 0 or percept_state[_x][_y][P] == 5 ): continue

            stench += 1
    else: 
        for position in GetNeighbor( current_position ): UpdatePercept( position, W, 0 )

    # Current position is breeze
    if( CheckState( current_position, B ) ):

        for _x, _y in GetNeighbor( current_position ):

            if( percept_state[_x][_y][0] == 1 ): continue
            if( percept_state[_x][_y][W] == 5 or percept_state[_x][_y][P] == 0 ): continue

            breeze += 1
    else: 
        for position in GetNeighbor( current_position ): UpdatePercept( position, P, 0 )
    
    # Update suspect
    percept_state[current_x][current_y] = ( visited, stench, wumpus, breeze, pit )

    # Update danger
    for position in GetNeighbor( current_position ):
        UpdateDanger( position, W )
        UpdateDanger( position, P )
    
    # Update neighbor
    for position in GetNeighbor( current_position ):
        UpdateHint( position, S )
        UpdateHint( position, B )

    # Entail danger
    EntailDanger( current_position )


#######################################################################################################################


Solver()

