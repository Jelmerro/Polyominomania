# Welcome to Polyominomania
# See the README.md and github.com/Jelmerro/Polyominomania for more details
# Released into the public domain, see UNLICENSE for details
__license__ = "UNLICENSE"

from random import SystemRandom

# Number of one-sided polyominoes with n cells https://oeis.org/A000988
A000988 = [
    None, 1, 1, 2, 7, 18, 60, 196, 704, 2500, 9189,
    33896, 126759, 476270, 1802312, 6849777, 26152418,
    100203194, 385221143, 1485200848, 5741256764,
    22245940545, 86383382827, 336093325058, 1309998125640,
    5114451441106, 19998172734786, 78306011677182,
    307022182222506, 1205243866707468, 4736694001644862
]


def generate(number):
    grid = []
    ynum = int(number / 2 + 0.5)
    # generate empty grid of desired size
    for _ in range(0, number):
        line = []
        for _ in range(0, ynum):
            line.append(0)
        grid.append(line)
    # start at random location
    x = SystemRandom().randrange(number)
    y = SystemRandom().randrange(ynum)
    grid[x][y] = 1
    # walk into a random direction for the amount of squares needed
    while sum(sum(grid, []), 0) != number:
        new_x = -1
        new_y = -1
        while new_x < 0 or new_y < 0 or new_x >= number or new_y >= ynum:
            new_x = x
            new_y = y
            if SystemRandom().choice([True, False]):
                new_x += SystemRandom().choice([1, -1])
                new_y = y
            else:
                new_x = x
                new_y += SystemRandom().choice([1, -1])
        x = new_x
        y = new_y
        grid[x][y] = 1
    # delete empty rows
    while sum(grid[0]) == 0:
        grid.pop(0)
    while sum(grid[len(grid)-1]) == 0:
        grid.pop(len(grid)-1)
    # clear columns left
    for _ in range(0, number):
        first_column_empty = True
        for i in range(0, len(grid)):
            if grid[i][0] == 1:
                first_column_empty = False
                break
        if not first_column_empty:
            break
        else:
            for i, _ in enumerate(grid):
                grid[i].pop(0)
    # clear columns right
    for _ in range(0, number):
        first_column_empty = True
        for i, _ in enumerate(grid):
            if grid[i][len(grid[i])-1] == 1:
                first_column_empty = False
                break
        if not first_column_empty:
            break
        for i, _ in enumerate(grid):
            grid[i].pop(len(grid[i])-1)
    return grid


def rotate(piece, clockwise=True):
    if clockwise:
        return [list(elem) for elem in list(zip(*piece[::-1]))]
    return [list(elem) for elem in list(zip(*piece))[::-1]]


def fix_rotation_position(piece, rotated):
    old_x, old_y = center_point(piece)
    new_x, new_y = center_point(rotated)
    x = old_x - new_x
    y = old_y - new_y
    return x, y


def center_point(piece):
    total_x = 0
    total_y = 0
    total_points = 0
    for y, _ in enumerate(piece):
        for x, _ in enumerate(piece[y]):
            if piece[y][x] == 1:
                total_x += x
                total_y += y
            total_points += 1
    average_x = total_x / total_points
    average_y = total_y / total_points
    fixed_x = weird_rounding(average_x)
    fixed_y = weird_rounding(average_y)
    return fixed_x, fixed_y


def weird_rounding(number):
    decimals = number - int(number)
    if decimals >= 0.5:
        return int(number) + 1
    return int(number)


def duplicate(pieces, piece):
    for _ in range(0, 4):
        if piece in pieces:
            return True
        piece = rotate(piece)
    return False


def generate_all(number):
    pieces = []
    while len(pieces) < A000988[number]:
        piece = generate(number)
        if not duplicate(pieces, piece):
            pieces.append(piece)
    return pieces


def piece_name(piece):
    name = ""
    piece_o = [[1, 1], [1, 1]]
    if piece == piece_o:
        name = "o"
    piece_i = [[1], [1], [1], [1]]
    if piece == piece_i:
        name = "i"
    piece_t = [
        [[0, 1], [1, 1], [0, 1]],
        [[1, 0], [1, 1], [1, 0]]
    ]
    if piece in piece_t:
        name = "t"
    piece_s = [[1, 0], [1, 1], [0, 1]]
    if piece == piece_s:
        name = "s"
    piece_z = [[0, 1], [1, 1], [1, 0]]
    if piece == piece_z:
        name = "z"
    piece_j = [
        [[0, 1], [0, 1], [1, 1]],
        [[1, 1], [1, 0], [1, 0]]
    ]
    if piece in piece_j:
        name = "j"
    piece_l = [
        [[1, 1], [0, 1], [0, 1]],
        [[1, 0], [1, 0], [1, 1]]
    ]
    if piece in piece_l:
        name = "l"
    return name


def color(piece, scheme):
    name = piece_name(piece)
    if not name:
        name = SystemRandom().choice(list("oitszjl"))
    colors = {
        "original": {
            "o": "ffff00",  # yellow
            "i": "00ffff",  # cyan
            "t": "aa00ff",  # purple
            "s": "00ff00",  # lime
            "z": "ff0000",  # red
            "j": "0000ff",  # blue
            "l": "ffa500"   # orange
        },
        "retro": {
            "o": "ff906b",
            "i": "666547",
            "t": "6fcb9f",
            "s": "ffe28a",
            "z": "fffeb3",
            "j": "f9402f",
            "l": "96d5ff"
        },
        "bootstrap": {
            "o": "f0ad41",
            "i": "5cb85c",
            "t": "d9534f",
            "s": "fff7f4",
            "z": "5bc0de",
            "j": "6c5196",
            "l": "428bca"
        },
        "gray": {
            "o": "444444",
            "i": "666666",
            "t": "888888",
            "s": "aaaaaa",
            "z": "cccccc",
            "j": "e8e8e8",
            "l": "ffffff"
        }
    }
    color = colors[scheme][name] + "ff"
    return tuple(int(color[i:i+2], 16) for i in (0, 2, 4, 6))


def supported_color_schemes():
    return ["original", "retro", "bootstrap", "gray"]


def install_times(number):
    if number < 6:
        time = "under a second"
    elif number == 6:
        time = "a few seconds"
    elif number == 7:
        time = "up to a minute"
    elif number == 8:
        time = "a few minutes"
    elif number == 9:
        time = "up to 30 minutes"
    elif number == 10:
        time = "up to 3 hours"
    else:
        time = "many days"
    return time
