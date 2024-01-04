from enum import Enum


class States(Enum):
    FORWARD = 0
    LEFT = 1
    RIGHT = 2
    GRAB = 3
    SHOOT = 4
    CLIMB = 5
    PERCEPT_PIT = 6
    PERCEPT_NO_PIT = 7
    PERCEPT_WUMPUS = 8
    PERCEPT_NO_WUMPUS = 9
    PERCEPT_WUMPUS_KILLED = 10
    KILLED_BY_WUMPUS = 11
    FALL_INTO_PIT = 12
    FIND_GOAL = 13
    DETECTED_PIT = 14
    DETECTED_WUMPUS = 15


class Directions(Enum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3


GOLD = 'G'
WUMPUS = 'W'
PIT = 'P'
BREEZE = 'B'
STENCH = 'S'
