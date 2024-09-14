import random
import os
import sys
import tty
import termios

def get_ch():
    """Wait for a single keypress on stdin."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
        if ch == '\x1b':
            ch += sys.stdin.read(2)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def init_board():
    board = [[0]*4 for _ in range(4)]
    add_new_tile(board)
    add_new_tile(board)
    return board

def add_new_tile(board):
    empty_cells = [(i, j) for i in range(4) for j in range(4) if board[i][j] == 0]
    if empty_cells:
        i, j = random.choice(empty_cells)
        board[i][j] = 4 if random.random() > 0.9 else 2

def draw_board(board, score):
    clear_screen()
    print(f"Score: {score}")
    print("+----+----+----+----+")
    for row in board:
        print("|".join(f"{num:^4}" if num > 0 else "    " for num in row) + "|")
        print("+----+----+----+----+")

def compress(board):
    new_board = []
    changed = False
    for row in board:
        new_row = [num for num in row if num != 0]
        new_row += [0] * (4 - len(new_row))
        if new_row != row:
            changed = True
        new_board.append(new_row)
    return new_board, changed

def merge(board):
    score = 0
    changed = False
    for row in board:
        for i in range(3):
            if row[i] != 0 and row[i] == row[i+1]:
                row[i] *= 2
                score += row[i]
                row[i+1] = 0
                changed = True
    return board, score, changed

def reverse(board):
    return [row[::-1] for row in board]

def transpose(board):
    return [list(row) for row in zip(*board)]

def move_left(board):
    board, changed1 = compress(board)
    board, score, changed2 = merge(board)
    board, _ = compress(board)
    return board, score, changed1 or changed2

def move_right(board):
    board = reverse(board)
    board, score, changed = move_left(board)
    board = reverse(board)
    return board, score, changed

def move_up(board):
    board = transpose(board)
    board, score, changed = move_left(board)
    board = transpose(board)
    return board, score, changed

def move_down(board):
    board = transpose(board)
    board, score, changed = move_right(board)
    board = transpose(board)
    return board, score, changed

def is_game_over(board):
    for i in range(4):
        for j in range(4):
            if board[i][j] == 0:
                return False
            if j < 3 and board[i][j] == board[i][j+1]:
                return False
            if i < 3 and board[i][j] == board[i+1][j]:
                return False
    return True

def main():
    board = init_board()
    score = 0
    while True:
        draw_board(board, score)
        if is_game_over(board):
            print("Game Over!")
            break
        print("Use arrow keys to move. Press 'q' to quit.")
        key = get_ch()
        if key == '\x1b[A':  # Up
            board, gained_score, changed = move_up(board)
        elif key == '\x1b[B':  # Down
            board, gained_score, changed = move_down(board)
        elif key == '\x1b[D':  # Left
            board, gained_score, changed = move_left(board)
        elif key == '\x1b[C':  # Right
            board, gained_score, changed = move_right(board)
        elif key in ('q', 'Q'):
            print("Goodbye!")
            break
        else:
            continue
        if changed:
            add_new_tile(board)
            score += gained_score

if __name__ == "__main__":
    main()
