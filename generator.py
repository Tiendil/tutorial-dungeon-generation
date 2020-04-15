
import argparse

from matplotlib import pyplot

parser = argparse.ArgumentParser(description='Generate dungeon.')

parser.add_argument('-f', '--filename', metavar='FILENAME', type=str, default='last.png', help='save result to file')
parser.add_argument('-s', '--show', action='store_true', default=False, help='show result in window')

arguments = parser.parse_args()


##############
# Core classes
##############

class Position:
    __slots__ = ('x', 'y')

    def __init__(self, x, y):
        self.x = x
        self.y = y


class Block:
    __slots__ = ('position',)

    def __init__(self, position):
        self.position = position

    def geometry_borders(self):
        return [((self.position.x, self.position.y), (self.position.x, self.position.y + 1)),
                ((self.position.x, self.position.y + 1), (self.position.x + 1, self.position.y + 1)),
                ((self.position.x + 1, self.position.y + 1), (self.position.x + 1, self.position.y)),
                ((self.position.x + 1, self.position.y), (self.position.x, self.position.y))]


#################
# Generation code
#################

block = Block(Position(0, 0))


####################
# Visualization code
####################

pyplot.axes().set_aspect('equal', 'datalim')

fig = pyplot.figure(1)

for border in block.geometry_borders():
    pyplot.plot(*zip(*border), color='#000000', linewidth=3, alpha=1)

if arguments.filename:
    pyplot.savefig(arguments.filename)

if arguments.show:
    pyplot.show()
