
import enum
import random
import argparse
import collections

from matplotlib import pyplot

parser = argparse.ArgumentParser(description='Generate dungeon.')

parser.add_argument('-f', '--filename', metavar='FILENAME', type=str, default='last.png', help='save result to file')
parser.add_argument('-s', '--show', action='store_true', default=False, help='show result in window')
parser.add_argument('-b', '--blocks', type=int, default=10, help='blocks in room')
parser.add_argument('-r', '--rooms', type=int, default=2, help='rooms in dungeon')

arguments = parser.parse_args()


##############
# Enumerations
##############

class DIRECTION(enum.Enum):
    LEFT = 1
    RIGHT = 2
    UP = 3
    DOWN = 4


#######
# Utils
#######

def random_color():
    return '#' + ''.join([random.choice('0123456789') for i in range(6)])


def points_at_circle(x, y, radius):
    points = set()

    for i in range(radius + 1):
        points.add((x + i, y + (radius - i)))
        points.add((x + i, y - (radius - i)))
        points.add((x - i, y + (radius - i)))
        points.add((x - i, y - (radius - i)))

    return points


def nearest_coordinates_generator(center_x, center_y, max_intersection_radius):
    for radius in range(max_intersection_radius):
        for x, y in points_at_circle(center_x, center_y, radius):
            yield (x, y)


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

    def area(self):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                yield Position(self.x + dx, self.y + dy)

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

    def move(self, dx, dy):
        self.position = self.position.move(dx, dy)


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

    def move(self, dx, dy):
        self.position = self.position.move(dx, dy)

        for border in self.borders.values():
            border.move(dx, dy)


class Room:
    __slots__ = ('blocks', 'color')

    def __init__(self):
        self.blocks = [Block(Position(0, 0))]
        self.color = random_color()

    def block_positions(self):
        return {block.position for block in self.blocks}

    def area_positions(self):
        area = set()

        for position in self.block_positions():
            area |= set(position.area())

        return area

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

    def rectangle(self):
        positions = self.block_positions()

        min_x, max_x, min_y, max_y = 0, 0, 0, 0

        for position in positions:
            min_x = min(position.x, min_x)
            min_y = min(position.y, min_y)
            max_x = max(position.x, max_x)
            max_y = max(position.y, max_y)

        return min_x, min_y, max_x, max_y

    def has_holes(self):
        min_x, min_y, max_x, max_y = self.rectangle()

        block_positions = self.block_positions()

        all_positions = set()

        # add additional empty cells around rectangle
        # to guaranty connectedness
        for x in range(min_x - 1, max_x + 2):
            for y in range(min_y - 1, max_y + 2):
                all_positions.add(Position(x, y))

        all_positions -= block_positions

        first_position = next(iter(all_positions))

        queue = collections.deque()

        queue.append(first_position)

        while queue:
            position = queue.popleft()

            if position not in all_positions:
                continue

            queue.extend(position.neighbours())

            all_positions.remove(position)

        return bool(all_positions)

    def is_intersect(self, room):
        return bool(self.area_positions() & room.block_positions())

    def move(self, dx, dy):
        for block in self.blocks:
            block.move(dx, dy)

    def base_position(self):
        return self.blocks[-1].position


class Dungeon:
    __slots__ = ('rooms',)

    def __init__(self):
        self.rooms = []

    def create_room(self, blocks):
        room = Room()

        for i in range(blocks):
            room.expand()

        return room

    def expand(self, blocks, max_intersection_radius=10):
        new_room = None

        while new_room is None or new_room.has_holes():
            print('try to generate room')
            new_room = self.create_room(blocks=blocks)

        for x, y in nearest_coordinates_generator(0, 0, max_intersection_radius):
            new_room.move(x - new_room.base_position().x,
                          y - new_room.base_position().y)

            for room in self.rooms:
                if room.is_intersect(new_room):
                    break

            else:
                break

        else:
            raise Exception('Can not place room')

        self.rooms.append(new_room)


#################
# Generation code
#################


dungeon = Dungeon()

for i in range(arguments.rooms):
    dungeon.expand(blocks=arguments.blocks)


####################
# Visualization code
####################

pyplot.axes().set_aspect('equal', 'datalim')

fig = pyplot.figure(1)

for room in dungeon.rooms:
    for border in room.geometry_borders():
        pyplot.plot(*zip(*border), color=room.color, linewidth=3, alpha=0.5)

if arguments.filename:
    pyplot.savefig(arguments.filename)

if arguments.show:
    pyplot.show()
