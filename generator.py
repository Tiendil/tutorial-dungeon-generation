
import random
import argparse


from matplotlib import pyplot

parser = argparse.ArgumentParser(description='Generate dungeon.')

parser.add_argument('-f', '--filename', metavar='FILENAME', type=str, default='last.png', help='save result to file')
parser.add_argument('-s', '--show', action='store_true', default=False, help='show result in window')
parser.add_argument('-b', '--blocks', type=int, default=15, help='block in room')

arguments = parser.parse_args()


##############
# Core classes
##############

class Position:
    __slots__ = ('x', 'y')

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def neighbours(self):
        return {Position(self.x - 1, self.y),
                Position(self.x, self.y - 1),
                Position(self.x + 1, self.y),
                Position(self.x, self.y + 1)}


class Block:
    __slots__ = ('position',)

    def __init__(self, position):
        self.position = position

    def geometry_borders(self):
        return [((self.position.x, self.position.y), (self.position.x, self.position.y + 1)),
                ((self.position.x, self.position.y + 1), (self.position.x + 1, self.position.y + 1)),
                ((self.position.x + 1, self.position.y + 1), (self.position.x + 1, self.position.y)),
                ((self.position.x + 1, self.position.y), (self.position.x, self.position.y))]


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
