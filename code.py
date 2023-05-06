# my modules
import numpy as np
import pygame
import sys
import math
import random

# my global variables
row_count = 6
column_count = 7
color1 = (0, 0, 255)   # Blue
color2 = (0, 0, 0)    # Black
color3 = (255, 0, 0)   # Red
color4 = (255, 255, 0)   # Yellow
player = 0
ai = 1
player_piece = 1
ai_piece = 2
window_length = 4
empty = 0

# Determine the screen size
square_size = 100
circle_radius = int(square_size / 2 - 5)
width = column_count * square_size
height = (row_count + 1) * square_size
size = (width, height)
screen = pygame.display.set_mode(size)

# my functions------------------------------------------------------------------------------

# create initial state array from zeros
def create_board():
    Board = np.zeros((row_count, column_count))
    return Board

# Check if the specified column contains free location
def is_valid_location(Board, col):
    return Board[row_count - 1][col] == 0

# Finds the last empty location in the specified column
def get_next_open_row(Board, col):
    for r in range(row_count):
        if Board[r][col] == 0:
            return r

# drop piece in specific location
def drop_piece(Board, row, col, piece):
    Board[row][col] = piece

# Flip the Board to start index from the end of the screen.
def print_board(Board):
    print(np.flip(Board, 0))

# to determine the winner
def winning_move(Board, piece):
    # Check horizontal locations for win
    for c in range(column_count - 3):
        for r in range(row_count):
            if Board[r][c] == piece and Board[r][c + 1] == piece and Board[r][c + 2] == piece and Board[r][c + 3] == piece:
                return True
    # Check vertical locations for win
    for c in range(column_count):
        for r in range(row_count - 3):
            if Board[r][c] == piece and Board[r + 1][c] == piece and Board[r + 2][c] == piece and Board[r + 3][c] == piece:
                return True
    # Check positively sloped diaganols
    for c in range(column_count - 3):
        for r in range(row_count - 3):
            if Board[r][c] == piece and Board[r + 1][c + 1] == piece and Board[r + 2][c + 2] == piece and Board[r + 3][c + 3] == piece:
                return True
    # Check negatively sloped diaganols
    for c in range(column_count - 3):
        for r in range(3, row_count):
            if Board[r][c] == piece and Board[r - 1][c + 1] == piece and Board[r - 2][c + 2] == piece and Board[r - 3][c + 3] == piece:
                return True


def evaluate_window(window, piece):
    score = 0
    opp_piece = player_piece
    if piece == player_piece:
        opp_piece = ai_piece
    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(empty) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(empty) == 2:
        score += 2
    if window.count(opp_piece) == 3 and window.count(empty) == 1:
        score -= 4
    return score

def score_position(Board, piece):
    score = 0
    # Score center column
    center_array = [int(i) for i in list(Board[:, column_count // 2])]
    center_count = center_array.count(piece)
    score += center_count * 3
    # Score Horizontal
    for r in range(row_count):
        row_array = [int(i) for i in list(Board[r, :])]
        for c in range(column_count - 3):
            window = row_array[c:c + window_length]
            score += evaluate_window(window, piece)
    # Score Vertical
    for c in range(column_count):
        col_array = [int(i) for i in list(Board[:, c])]
        for r in range(row_count - 3):
            window = col_array[r:r + window_length]
            score += evaluate_window(window, piece)
    # Score positive sloped diagonal
    for r in range(row_count - 3):
        for c in range(column_count - 3):
            window = [Board[r + i][c + i] for i in range(window_length)]
            score += evaluate_window(window, piece)
    # Score negatively sloped diagonal
    for r in range(row_count - 3):
        for c in range(column_count - 3):
            window = [Board[r + 3 - i][c + i] for i in range(window_length)]
            score += evaluate_window(window, piece)
    return score

# return a list with all valid locations in a board
def get_valid_locations(Board):
    valid_locations = []
    for col in range(column_count):
        if is_valid_location(Board, col):
            valid_locations.append(col)
    return valid_locations

# Draw the screen
def draw_board(Board):
    for c in range(column_count):
        for r in range(row_count):
            pygame.draw.rect(screen, color1, (c * square_size, r * square_size + square_size, square_size, square_size))
            pygame.draw.circle(screen, color2, (int(c * square_size + square_size / 2), int(r * square_size + square_size + square_size / 2)), circle_radius)
    for c in range(column_count):
        for r in range(row_count):
            if Board[r][c] == player_piece:
                pygame.draw.circle(screen, color3, (int(c * square_size + square_size / 2), height - int(r * square_size + square_size / 2)), circle_radius)
            elif Board[r][c] == ai_piece:
                pygame.draw.circle(screen, color4, (int(c * square_size + square_size / 2), height - int(r * square_size + square_size / 2)), circle_radius)
    pygame.display.update()

# to determine end of game
def is_terminal_node(Board):
    return winning_move(Board, player_piece) or winning_move(Board, ai_piece) or len(get_valid_locations(Board)) == 0

# the algo
def minimax(Board, depth, alpha, beta, maximizingPlayer):
    valid_locations = get_valid_locations(Board)
    is_terminal = is_terminal_node(Board)
    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(Board, ai_piece):
                return (None, 100000000000000)
            elif winning_move(Board, player_piece):
                return (None, -10000000000000)
            else:  # Game is over, no more valid moves
                return (None, 0)
        else:  # Depth is zero
            return (None, score_position(Board, ai_piece))
    if maximizingPlayer:
        value = -math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(Board, col)
            b_copy = Board.copy()
            drop_piece(b_copy, row, col, ai_piece)
            new_score = minimax(b_copy, depth - 1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value

    else:  # Minimizing player
        value = math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(Board, col)
            b_copy = Board.copy()
            drop_piece(b_copy, row, col, player_piece)
            new_score = minimax(b_copy, depth - 1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value

# main--------------------------------------------------------------------------------

# create object from board
Board = create_board()
print_board(Board)

# initialize all imported pygame modules
pygame.init()

# Display the draw screen
draw_board(Board)
pygame.display.update()

myfont = pygame.font.SysFont("monospace", 75)

game_over = False
turn = random.randint(player, ai)
while not game_over:
    # When you click on the X, close the game
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        # To draw the circle at the beginning of the game
        if event.type == pygame.MOUSEMOTION:
            pygame.draw.rect(screen, color2, (0, 0, width, square_size))
            posx = event.pos[0]
            if turn == player:
                pygame.draw.circle(screen, color3, (posx, int(square_size / 2)), circle_radius)
        pygame.display.update()

        if event.type == pygame.MOUSEBUTTONDOWN:
            pygame.draw.rect(screen, color2, (0, 0, width, square_size))
            # Ask for Player 1 Input
            if turn == player:
                posx = event.pos[0]
                col = int(math.floor(posx / square_size))
                if is_valid_location(Board, col):
                    row = get_next_open_row(Board, col)
                    drop_piece(Board, row, col, player_piece)
                    if winning_move(Board, player_piece):
                        label = myfont.render("Player 1 wins!!", 1, color3)
                        screen.blit(label, (40, 10))
                        game_over = True
                    turn += 1
                    turn = turn % 2
                    print_board(Board)
                    draw_board(Board)

    # AI Input
    if turn == ai and not game_over:
        # col = pick_best_move(board, AI_PIECE)
        col, minimax_score = minimax(Board, 5, -math.inf, math.inf, True)
        if is_valid_location(Board, col):
            row = get_next_open_row(Board, col)
            drop_piece(Board, row, col, ai_piece)
            if winning_move(Board, ai_piece):
                label = myfont.render("Player 2 wins!!", 1, color4)
                screen.blit(label, (40, 10))
                game_over = True
            print_board(Board)
            draw_board(Board)
            turn += 1
            turn = turn % 2

    if game_over:
        pygame.time.wait(3000)
