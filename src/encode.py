'''
To make the operation faster (O(1) instead of O(n)),
We encode each state into a number using biwise operation
The state has 6 bits:

- Bit 0: agent
- Bit 1: wumpus
- Bit 2: pit
- Bit 3: gold
- Bit 4: breeze
- Bit 5: stench

From this, we implement the function encode_bits
and other funtions to get the value of each bit

'''


def encode_bits(agent, wumpus, pit, gold, breeze, stench):
    state = 0
    state |= agent
    state |= wumpus << 1
    state |= pit << 2
    state |= gold << 3
    state |= breeze << 4
    state |= stench << 5
    return state


def has_agent(state):
    return state & 1 == 1


def has_wumpus(state):
    return (state >> 1) & 1 == 1


def has_pit(state):
    return (state >> 2) & 1 == 1


def has_gold(state):
    return (state >> 3) & 1 == 1


def get_breeze(state):
    return (state >> 4) & 1 == 1


def get_stench(state):
    return (state >> 5) & 1 == 1
