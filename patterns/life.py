"""
Author:   Karl Sims. 2017.
Goal:     Implement 3D version of Conway's Game of Life for LED cubes.
"""
import random


class Pattern(object):

    def init(self):
        # self.double_buffer = True
        self.life = CubeLife(size=self.cube.size, 
                             limit=100, 
                             new_state_fn=random_blast,
                             next_generation_fn=next_generation_3d)
        return 1.0/8 # time between ticks.

    def tick(self):
        self.cube.clear()
        for xyz_position, color in self.life.successors():
            self.cube.set_pixel(xyz_position, color)




class CubeLife(object):
    "Implements interface for generating successor states in conways game of life."
    
    def __init__(self, size, limit, new_state_fn, next_generation_fn, limited=False):
        self.size = size
        self.limit = limit
        self.limited = False
        self.new_state_fn = new_state_fn
        self.next_generation_fn = next_generation_fn
        # self.color_change = self.__color_change_2dim_secondary
        self.color_change = self.__color_change
        self.__restart()

    def successors(self):
        generations = self.__life()
        for (position, rgb) in next(generations).items():
            yield (position, rgb)

    def __life(self):
        while True:
            if self.__done():
                self.__restart()
            else:
                self.count += 1
                self.state = self.next_generation_fn(self.state, self.size)
            self.patterns.append(self.state)
            self.color_change()
            for k in self.state:
                self.visited[k] = self.color1
            yield self.visited

    def __restart(self):
        self.count = 0
        self.visited = dict()
        self.patterns = []
        self.state = set()
        self.color1, self.color2 = new_colors()
        self.cDeltas = color_differences(self.color1, self.color2, 10)
        self.state = self.new_state_fn(self.size)

    def __done(self):
        if self.limited and self.count == self.limit:
            raise StopIteration
        if len(self.patterns) >= 6:
            self.patterns.pop(0)
            # We dont want to be stuck on short repeating patterns forever.
            # This catches some cases, including solid states but not all.
            if self.patterns[-3] == self.state:
                return True
        return self.count == self.limit

    """
    TODO: deside color change function for good.
    
    NOTES:
    __color_change:        
        probs a bit mental and random looking. works good in 2d.
        kinda hides the the fact its life. but i guess you wont see
        that here anyway.
    __color_change_2dim_secondary:
        Kinda nice and chill not as mental as __color_change.
    __color_dim:
        kinda nice and chill.
    __color_change_2black: 
        probs a bit boring. if used can streamline visited.
    
    Replace self.color_change in __init__ with a color change function of choice.
    """

    def __color_change(self):
        """Subtract cDeltas from visited colors to do a pesudo transition
        to secondary color. create echo effect to keep constant motion.
        This is done by Allowing colors decrement/increment till they
        reach the limit of valid rgb values then switch them to the set
        secondary color, this loop repeats till visited is reset."""
        dr, dg, db = self.cDeltas
        c2 = self.color2
        for k, (r, g, b) in self.visited.items():
            (r, g, b) = (r-dr, g-dg, b-db)
            new_rgb = tuple([c2[i] if c > 205 else c2[i] if c < 20 else 
                            int(c) for i, c in enumerate((r, g, b))])
            self.visited[k] = new_rgb

    def __color_change_2black(self):
        "just turn all visited squares to black."
        for k, value in self.visited.items():
            self.visited[k] = (0,0,0)

    def __color_dim(self):
        "fade out visited co-ords"
        (r1, g1, b1) = self.color2
        for k, (r, g, b) in self.visited.items():
            self.visited[k] = (r//2, g//2, b//2)

    def __color_change_2dim_secondary(self):
        "fade out visited co-ords"
        (r1, g1, b1) = self.color2
        for k, (r, g, b) in self.visited.items():
            self.visited[k] = (r1//4, g1//4, b1//4)



"""
Basic Life implementation in 3d.

Fundamental 'Life' Rules in square land:
1) Any live cell with fewer than two live neighbors dies, 
   as if caused by underpopulation.
2) Any live cell with more than three live neighbors dies, 
   as if by overcrowding.
3) Any live cell with two or three live neighbors lives on 
   to the next generation.
4) Any dead cell with exactly three live neighbors becomes 
   a live cell.

More info: http://web.stanford.edu/~cdebs/GameOfLife/

Another's ideas about creating versions in cube land:
http://www.complex-systems.com/pdf/01-3-1
Current neighbour rules are tentative. Tweaking the inital state function
may also be helpful in ensuring a got life / failed-life ratio.

TODO: choose for good neighbour rules.
"""

def next_generation_3d(state, size=None):
    """nextGeneration(set: state, size=None): set: {(ints: x, y, z), ...};
    Following the game rules return a successive state from any given state 
    on an infinite or finite plane. Adapted function version for 3d."""
    new_state = set()
    for cell in state:
        cell_neighbours = neighbours_3d(cell)
        if len(state & cell_neighbours) in (3, 4, 5): # rule 3 / (1 & 2)
            new_state.add(cell)
        for cn in cell_neighbours:
            if len(state & neighbours_3d(cn)) is 5: # rule 4
                new_state.add(cn)
    return (new_state if not size else constrain_3d(new_state, size))


def neighbours_3d(cell):
    """neighbours(tuple: cell): set: {(ints: x, y, z), ...};
    returns a set of co-ordinates +/- 1 from a given position."""
    (x, y, z) = cell
    return set((x + dx, y + dy, z + dz) for dx, dy, dz in deltas_3d)


deltas_3d = [(x, y, z) for x in range(-1, 2) 
                       for y in range(-1, 2)
                       for z in range(-1, 2) 
                       if not (x == y == z == 0)]


# Random Utilies / Initial State funcitons:

__rand = random.randint

def random_state(size):
    "return x, y, z co-ords that could be anywhere in state space."
    return set((__rand(0,size-1), __rand(0,size-1), __rand(0,size-1)) 
                for x in range(__rand(size, size*3)))

def constrained_random_state(size):
    "return x, y, z co-ords limiting to smaller part of the state space."
    edge = int(size/2.2)
    return set((__rand(edge, size - edge), 
                __rand(edge, size - edge),
                __rand(edge, size - edge))
                for x in range(30))

def random_state3d(size):
    "return x, y, z co-ords with +-1 to increase changes of starting life"
    return set((x+d, y+d, z+d) for d in range(-1, 2) 
               for x, y, z in constrained_random_state(size)) | random_state(size)

def random_blast(size):
    "concentrated center scattered rest."
    return random_state3d(size) | random_state(size)


# Color Utilies:

def new_colors():
    "return 2 random rgb color from material design colors"
    return random.choice(material_colors)

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

def color_differences(c1, c2, steps):
    "Calculate step size for a given amount of steps between 2 rgb colors"
    (r1, g1, b1), (r2, g2, b2) = (c1, c2)
    return ((r1 - r2)/steps, (g1 - g2)/steps, (b1 - b2)/steps)

def constrain_3d(S, s):
    "Make little s within big S and 0"
    return set((x, y, z) for x, y, z in S 
               if 0 <= x < s and 0 <= y < s and 0 <= z < s)


