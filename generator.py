
import enum
import random
import argparse


from matplotlib import pyplot

parser = argparse.ArgumentParser(description='Generate dungeon.')

parser.add_argument('-f', '--filename', metavar='FILENAME', type=str, default='last.png', help='save result to file')
parser.add_argument('-s', '--show', action='store_true', default=False, help='show result in window')
parser.add_argument('-b', '--blocks', type=int, default=15, help='block in room')

arguments = parser.parse_args()


##############
# Enumerations
##############

class DIRECTION(enum.Enum):
    LEFT = 1
    RIGHT = 2
    UP = 3
    DOWN = 4


##############
# Core classes
##############

class Position:
    __slots__ = ('x', 'y')

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __hash__(self):
        return hash((self.x, self.y))

    def __eq__(self, other):
        return (self.x, self.y) == (other.x, other.y)

    def __ne__(self, other):
        return not self.__eq__(other)

    def neighbours(self):
        return {Position(self.x - 1, self.y),
                Position(self.x, self.y - 1),
                Position(self.x + 1, self.y),
                Position(self.x, self.y + 1)}

    def move(self, dx, dy):
        return Position(self.x + dx, self.y + dy)

    def point(self):
        return (self.x, self.y)


class Border:
    __slots__ = ('position', 'direction', 'internal')

    def __init__(self, position, direction):
        self.position = position
        self.direction = direction
        self.internal = False

    def __eq__(self, other):
        return (self.position, self.direction) == (other.position, other.direction)

    def __ne__(self, other):
        return not self.__eq__(other)

    def mirror(self):
        if self.direction == DIRECTION.LEFT:
            return Border(self.position.move(-1, 0), DIRECTION.RIGHT)

        if self.direction == DIRECTION.RIGHT:
            return Border(self.position.move(1, 0), DIRECTION.LEFT)

        if self.direction == DIRECTION.UP:
            return Border(self.position.move(0, 1), DIRECTION.DOWN)

        if self.direction == DIRECTION.DOWN:
            return Border(self.position.move(0, -1), DIRECTION.UP)

    def geometry_borders(self):
        if self.direction == DIRECTION.LEFT:
            return [self.position.move(0, 0).point(),
                    self.position.move(0, 1).point()]

        if self.direction == DIRECTION.RIGHT:
            return [self.position.move(1, 1).point(),
                    self.position.move(1, 0).point()]

        if self.direction == DIRECTION.UP:
            return [self.position.move(0, 1).point(),
                    self.position.move(1, 1).point()]

        if self.direction == DIRECTION.DOWN:
            return [self.position.move(1, 0).point(),
                    self.position.move(0, 0).point()]


class Block:
    __slots__ = ('position', 'borders')

    def __init__(self, position):
        self.position = position

        self.borders = {DIRECTION.RIGHT: Border(position, DIRECTION.RIGHT),
                        DIRECTION.LEFT: Border(position, DIRECTION.LEFT),
                        DIRECTION.UP: Border(position, DIRECTION.UP),
                        DIRECTION.DOWN: Border(position, DIRECTION.DOWN)}

    def geometry_borders(self):
        return [border.geometry_borders()
                for border in self.borders.values()
                if not border.internal]

    def sync_borders_with(self, block):
        for own_border in self.borders.values():
            for other_border in block.borders.values():
                if own_border.mirror() == other_border:
                    own_border.internal = True
                    other_border.internal = True


class Room:
    __slots__ = ('blocks',)

    def __init__(self):
        self.blocks = [Block(Position(0, 0))]

    def block_positions(self):
        return {block.position for block in self.blocks}

    def allowed_new_block_positions(self):
        allowed_positions = set()

        for block in self.blocks:
            allowed_positions |= block.position.neighbours()

        allowed_positions -= self.block_positions()

        return allowed_positions

    def expand(self):
        new_position = random.choice(list(self.allowed_new_block_positions()))

        new_block = Block(new_position)

        for block in self.blocks:
            block.sync_borders_with(new_block)

        self.blocks.append(new_block)

    def geometry_borders(self):
        borders = []

        for block in self.blocks:
            borders.extend(block.geometry_borders())

        return borders


#################
# Generation code
#################

room = Room()

for i in range(arguments.blocks):
    room.expand()


####################
# Visualization code
####################

pyplot.axes().set_aspect('equal', 'datalim')

fig = pyplot.figure(1)

for border in room.geometry_borders():
    pyplot.plot(*zip(*border), color='#000000', linewidth=3, alpha=1)

if arguments.filename:
    pyplot.savefig(arguments.filename)

if arguments.show:
    pyplot.show()
