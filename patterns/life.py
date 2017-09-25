"""
Author:   Karl Sims. 2017.
Goal:     Implement 3D version of Conway's Game of Life for LED cubes.


Alternative rules for 'Life' in 3 dimensions used here are as follows:

    1) Any live cell with fewer than 3 live neighbors dies, 
       as if caused by underpopulation.

    2) Any live cell with more than 5 live neighbors dies, 
       as if by overcrowding.

    3) Any live cell with 3, 4, 5 live neighbors lives on 
       to the next generation.

    4) Any live cell with exactly 5 live neighbors develops a
        mutation causing it to change color.

    5) Any dead cell with exactly 5 live neighbors becomes 
       a live cell. 


Infomation on classic version of 'Life': https://goo.gl/CR7fbR
pdf Essay on 'Life' in 3 dimensions: https://goo.gl/j6BGaA
"""
import random


class Pattern(object):

    def init(self):
        self.double_buffer = True # dosent clear propperly.
        self.life = CubeLife(size=self.cube.size, 
                             limit=100, 
                             new_state=random_blast,
                             next_generation=next_generation_3d)
        return 1.0/8 # time between ticks.

    def tick(self):
        self.cube.clear()
        for (x, y, z), color in self.life.successors():
            self.cube.set_pixel((x, y, z), color)




class CubeLife(object):
    "Implements interface for generating successor states in conways game of life."
    
    def __init__(self, size, limit, new_state, next_generation, limited=False):
        self.size = size
        self.limit = limit
        # Add generation functions.
        self.new_state = new_state
        self.next_gen = next_generation
        # set initial values.
        self.__restart()

    def successors(self):
        for position, mutation in next(self.__life()):
            yield ((position, self.color2) if mutation else
                   (position, self.color1))

    def __life(self):
        "yield whole generations of life forever."
        while True:
            if self.__done():
                self.__restart()
            else:
                self.state = self.next_gen(self.state, self.size)
                self.count += 1
                self.patterns.append(self.state)
            yield self.state

    def __restart(self):
        "Set initial values for each new game of life"
        self.count = 0
        self.patterns = []
        self.state = set()
        self.color1, self.color2 = new_colors()
        # Set the inital state from which to spawn Life.
        self.state = self.new_state(self.size)

    def __done(self):
        if len(self.patterns) >= 6:
            self.patterns.pop(0)
            # We dont want to be stuck on short repeating patterns forever.
            # This catches some cases, including solid states but not all.
            if self.patterns[-3] == self.state:
                return True
        return self.count == self.limit


# Generating new Generations for life:
# Code adapted slightly implimentation in 2d. Main differences include:
# constrained state space, returns ((x, y, z), bool: mutation)

def next_generation_3d(state, size):
    """nextGeneration(set: state, size=None): set: {(ints: x, y, z), ...};
    Following the game rules return a successive state from any given state 
    on an infinite or finite plane. Adapted function version for 3d."""
    new_state = set()
    for cell in state:
        cell_neighbours = neighbours_3d(cell)
        if len(state & cell_neighbours) in (3, 4): # rule 3 / (1 & 2)
            new_state.add(cell)
        elif len(state & cell_neighbours) is 5: # rule 4 they get sick
            c, _ = cell
            new_state.add((c, True))
        for cn in cell_neighbours: # rule 4
            if len(state & neighbours_3d(cn)) is 5: 
                new_state.add(cn)
    return constrain(new_state, size)


def neighbours_3d(cell):
    """neighbours(tuple: cell): set: {(ints: x, y, z), ...};
    returns a set of co-ordinates +/- 1 from a given position."""
    (x, y, z), mute = cell
    return set(((x + dx, y + dy, z + dz), mute) for dx, dy, dz in deltas_3d)


deltas_3d = [(x, y, z) for x in range(-1, 2) 
                       for y in range(-1, 2)
                       for z in range(-1, 2) 
                       if not (x == y == z == 0)]


def constrain(S, s):
    return set(((x, y, z), mute) for (x, y, z), mute in S
               if 0 <= x < s and 0 <= y < s and 0 <= z < s)


# Random Utilies / Initial State funcitons:

def random_blast(size):
    "concentrated center scattered rest."
    edge = int(size/2.2)
    bundle = set(((__rand(edge, size - edge-1), 
                   __rand(edge, size - edge-1),
                   __rand(edge-1, size - edge)), False)
                 for position in range(8))
    scatter = set(((__rand(0,size-1), 
                    __rand(0,size-1), 
                    __rand(0,size-1)), False) 
                  for x in range(__rand(size, size*3)))
    return (bundle | scatter)

__rand = random.randint


# Color Utilies:

new_colors = lambda: random.choice(material_colors)

material_colors = [
    ((96,125,139), (213,0,0)),
    ((48,79,254), (213,0,0)),
    ((213,0,0), (48,79,254)),
    ((170,0,255), (0,145,234)),
    ((0,145,234), (170,0,255)),
    ((46,125,50), (255,143,0)),
    ((96,125,139), (139,195,74)),  # lime and blue grey
    ((139,195,74), (96,125,139)),  # lime and blue grey
    ((98,0,234), (0,121,107)),     # deep purple teal
    ((0,191,165), (98,0,234)),     # dark teal deep purple
]


