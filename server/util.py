

def move_right(x, y):
    return x + 1, y
def move_down(x, y):
    return x, y - 1
def move_left(x, y):
    return x - 1, y
def move_up(x, y):
    return x, y + 1
moves = [move_right, move_down, move_left, move_up]

def spiral(end,pos):
    from itertools import cycle
    _moves = cycle(moves)
    times_to_move = 1
    n = 1
    yield pos
    while True:
        for _ in range(2):
            move = next(_moves)
            for _ in range(times_to_move):
                if n >= end:
                    return
                pos = move(*pos)
                n+=1
                yield pos

            times_to_move += 1