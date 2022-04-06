#!/usr/bin/env python3

import sys

TETROMINO = {
    'I': [(0, 0), (0, 1), (0, 2), (0, 3)],
    'O': [(0, 0), (0, 1), (1, 0), (1, 1)],
    'T': [(0, 0), (1, 0), (2, 0), (1, 1)],
    'J': [(0, 0), (1, 0), (0, 1), (0, 2)],
    'L': [(0, 0), (1, 0), (1, 1), (1, 2)],
    'S': [(0, 0), (0, 1), (1, 1), (1, 2)],
    'Z': [(0, 0), (1, 0), (1, 1), (2, 1)]
}


def rotate(piece):
    rotation = [(-y, x) for (x, y) in piece]
    min_x = min(x for (x, y) in rotation)
    min_y = min(y for (x, y) in rotation)
    return sorted((x - min_x, y - min_y) for (x, y) in rotation)


def build_rotation_map():
    r_map = {}
    for tile in TETROMINO.keys():
        rotations = []
        if tile == 'O':  # has no unique rotations
            rotations.append(TETROMINO[tile])
        elif tile in ['I', 'S', 'Z']:  # has two unique rotations
            rotations.append(TETROMINO[tile])
            rotations.append(rotate(TETROMINO[tile]))
        else:  # all else have 4
            r = TETROMINO[tile]
            for i in range(4):
                rotations.append(r)
                r = rotate(r)
        r_map[tile] = rotations
    return r_map


ROTATION_MAP = build_rotation_map()


def build_color_map(board_x, board_y):
    """
    :param board_x: rows
    :param board_y: columns
    :return: colour map with the filled indexes as white
    """
    c_board = [['b' for y in range(board_y)] for x in range(board_x)]
    for y in range(board_y):
        for x in range(board_x):
            if (y + x) % 2 == 0:
                c_board[x][y] = 'w'
    c_map = {
        'board': c_board,
        'num_white': 0,
        'num_black': 0,
        'num_t': 0
    }
    return c_map


def is_solveable(pieces, board_space):
    """
    :param pieces: an array with some tetrominos
    :param board_space: the 2D array
    :return: True or False: True if the algorithm can continue, False otherwise
    """
    if board_space != len(pieces) * 4:
        return False
    num_t = len([p for p in pieces if p == 'T'])
    if num_t % 2 != 0:
        return False
    return True


def print_board(board, board_x, board_y):
    for y in range(board_y):
        for x in range(board_x):
            print(board[x][y], end=' ')
        print('')


def get_upper_leftmost_empty_square(board, board_x, board_y):
    for y in range(board_y):
        for x in range(board_x):
            if board[x][y] == '.':
                return (x, y)
    return None


def overlaps(pos_x, pos_y, piece, board):
    # shift piece left one if upper-left corner of piece (0, 0) is empty
    if piece[0] == (0, 1) or piece[0] == (0, 2):
        x = pos_x - 1
    else:
        x = pos_x
    for point in piece:
        try:
            xp = x + point[0]
            yp = pos_y + point[1]
            if xp < 0 or yp < 0 or board[xp][yp] != '.':
                return True
        except IndexError:
            return True  # outside of board grid
    return False


def place(pos_x, pos_y, tile, piece, value, board, c_map):
    # shift piece left one if upper-left corner of piece (0, 0) is empty
    if piece[0] == (0, 1) or piece[0] == (0, 2):
        x = pos_x - 1
    else:
        x = pos_x

    # used for t-pruning
    if tile == 'T':  # update the color map if the tile placed is a 'T'
        if value == '.':
            c_map['num_t'] = c_map['num_t'] - 1
        else:
            c_map['num_t'] = c_map['num_t'] + 1
        for point in piece:
            xc = x + point[0]
            yc = pos_y + point[1]
            if value == '.':
                if c_map['board'][xc][yc] == 'w':
                    c_map['num_white'] = c_map['num_white'] - 1
                else:
                    c_map['num_black'] = c_map['num_black'] - 1
            else:
                if c_map['board'][xc][yc] == 'w':
                    c_map['num_white'] = c_map['num_white'] + 1
                else:
                    c_map['num_black'] = c_map['num_black'] + 1

    for point in piece:
        xp = x + point[0]
        yp = pos_y + point[1]
        board[xp][yp] = value


def t_prune(pos_x, pos_y, rp, c_map):
    c_w = c_map['num_white']
    c_b = c_map['num_black']

    # shift piece left one if upper-left corner of piece (0, 0) is empty
    if rp[0] == (0, 1) or rp[0] == (0, 2):
        x = pos_x - 1
    else:
        x = pos_x

    for point in rp:
        xc = x + point[0]
        yc = pos_y + point[1]
        if c_map['board'][xc][yc] == 'w':
            c_w += 1
        else:
            c_b += 1
    if (c_w != c_b) and (c_map['num_t'] != 0) and (c_map['num_t'] % 2 != 0):
        return True
    return False


def solve(board, board_x, board_y, pieces, value, c_map):
    """

    :param board: the 2D board
    :param board_x: rows
    :param board_y: colums
    :param pieces: the tetrominoes
    :param value: alphabets used to fill the board
    :param c_map: the coloured map
    :return: True if the full board is white, False else.
    """
    if len(pieces) == 0:
        return True
    pos_x, pos_y = get_upper_leftmost_empty_square(board, board_x, board_y)
    placed = True
    previous_piece = None
    for tile in pieces:
        num_rotations = 0
        if tile == previous_piece and placed is False:
            continue
        for rp in ROTATION_MAP[tile]:
            num_rotations += 1
            if overlaps(pos_x, pos_y, rp, board):
                continue
            if tile == 'T' and t_prune(pos_x, pos_y, rp, c_map):
                if num_rotations == 4:  # 'T' couldn't be placed
                    placed = False
                    previous_piece = tile
                continue
            place(pos_x, pos_y, tile, rp, value, board, c_map)
            # make a new copy of the pieces list without the placed piece
            new_pieces = [p for p in pieces]
            new_pieces.remove(tile)
            value = chr(ord(value) + 1)
            solved = solve(board, board_x, board_y, new_pieces, value, c_map)
            if solved:
                return True
            place(pos_x, pos_y, tile, rp, '.', board, c_map)  # unplace piece
            value = chr(ord(value) - 1)
            placed = False  # remember that this piece couldn't be placed
            previous_piece = tile
    return False


def parse_puzzle(puzzle):
    """
    Takes in a puzzle which is an array and returns the board setup with row and column number,
    number of pieces left and the board configuration
    """
    board_x = int(puzzle.split()[1].strip())
    board_y = int(puzzle.split()[0].strip())
    pieces_string = puzzle.split()[2].strip()
    pieces = sorted([p for p in pieces_string])
    board = [['.' for y in range(board_y)] for x in range(board_x)]
    board_space = board_x * board_y
    return board_y, board_x, pieces, board_space, board


def main():
    puzzles_to_solve = sys.stdin.readlines()
    count = 0
    for puzzle in puzzles_to_solve:
        board_y, board_x, pieces, board_space, board = parse_puzzle(puzzle)
        x = int((board_x * board_y) / 20)
        if is_solveable(pieces, board_space) is False:
            continue
        else:
            if ('T' in pieces) and ('I' in pieces) and ('O' in pieces) and (
                        ('J' in pieces) or ('L' in pieces)) and (('S' in pieces) or ('Z' in pieces)):
                if (pieces.count('T') == x) and (pieces.count('I') == x) and (pieces.count('O') == x) and (
                            pieces.count('J') + pieces.count('L') == x) and (
                            pieces.count('S') + pieces.count('Z') == x):
                    color_map = build_color_map(board_x, board_y)  # used for 'T-pruning'
                    solved = solve(board, board_x, board_y, pieces, 'a', color_map)
                    if solved:
                        print_board(board, board_x, board_y)
                        print('columns: {}'.format(board_x))
                        print('rows   : {}'.format(board_y))
                        print('pieces : {}'.format(pieces))
                        count = count + 1
                        print('------------------------------------------------------------------------')
    if count > 1:
        print('Yes, there exists a packing for k collection of tetrominoes into a rectangle! ')
    else:
        print('No, there exists no combination!')
    print('---------END----------')


if __name__ == '__main__':
    main()
