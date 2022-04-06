#!/usr/bin/env python3

import itertools
import sys

pieces = ['I', 'T', 'O', 'Z', 'S', 'L', 'J']
x = int(sys.argv[1])
y = int(sys.argv[2])
size = int((x * y) / 4)
possible_puzzles = list(itertools.combinations_with_replacement(pieces, size))
for puzzle in possible_puzzles:
    p = ''.join(puzzle)
    print('{} {} {}'.format(x, y, p))
