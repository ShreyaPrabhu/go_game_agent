import sys
from copy import deepcopy

PLAYER_1 = 1
PLAYER_2 = 2
PLAYER1_DEAD_PIECES_COUNT = 0
PLAYER2_DEAD_PIECES_COUNT = 0
BOARD_SIZE = 5
REWARD = 5
PENALTY = 8
BEST_START_POSITION = [(2,2)]

def set_player_dead_pieces_count(player, dead_count):
    global PLAYER1_DEAD_PIECES_COUNT
    global PLAYER2_DEAD_PIECES_COUNT
    if(player == 1):
        PLAYER1_DEAD_PIECES_COUNT = PLAYER1_DEAD_PIECES_COUNT + dead_count
    else:
        PLAYER2_DEAD_PIECES_COUNT = PLAYER2_DEAD_PIECES_COUNT + dead_count

def get_unique_list(list):
    res = []
    for i in list:
        if i not in res:
            res.append(i)
    return res

# from read.py
def read_input(path):
    with open(path, 'r') as f:
        lines = f.readlines()
        player = int(lines[0])
        previous_board = [[int(x) for x in line.rstrip('\n')] for line in lines[1:BOARD_SIZE+1]]
        current_board = [[int(x) for x in line.rstrip('\n')] for line in lines[BOARD_SIZE+1: 2*BOARD_SIZE+1]]
        return player, previous_board, current_board

# from write.py
def write_output(action):
    outputfilename = "output.txt"
    with open(outputfilename, 'w') as ouputfile:
        if action == "PASS":
            ouputfile.write("PASS")
        else:
            ouputfile.write(str(action[0]) + "," + str(action[1]))

def position_exists_on_board(row, col):
    if(row < 0 or col < 0 or row >= BOARD_SIZE or col >= BOARD_SIZE):
        return False
    else:
        return True

def get_adjacent_neighbours(row, col):
    adjacent_neighbours = []
    if(position_exists_on_board(row+1, col)):
        adjacent_neighbours.append((row+1,col))
    if(position_exists_on_board(row-1, col)):
        adjacent_neighbours.append((row-1,col))
    if(position_exists_on_board(row, col+1)):
        adjacent_neighbours.append((row,col+1))
    if(position_exists_on_board(row, col-1)):
        adjacent_neighbours.append((row,col-1))
    return adjacent_neighbours

def find_contiguous_blocks(i, j, board, player):
    stack = [(i, j)]
    contiguous_blocks = []
    while stack:
        position = stack.pop()
        contiguous_blocks.append(position)
        adjacent_neighbours = get_adjacent_neighbours(position[0], position[1])
        adjacent_blocks = []
        for adj_neigh in adjacent_neighbours:
            if board[adj_neigh[0]][adj_neigh[1]] == player:
                adjacent_blocks.append(adj_neigh)
        for blocks in adjacent_blocks:
            if blocks not in stack and blocks not in contiguous_blocks:
                stack.append(blocks)
    return contiguous_blocks

def does_liberty_exists(i, j, board, player):
    liberties = get_liberty_positions(i, j, board, player)
    if liberties is not None and len(liberties) > 0:
        return True
    else:
        return False

def get_liberty_positions(i, j,board,player):
    liberties = []
    contiguous_blocks = find_contiguous_blocks(i, j,board,player)
    for blocks in contiguous_blocks:
        neighbours = get_adjacent_neighbours(blocks[0], blocks[1])
        for neighbour in neighbours:
            if board[neighbour[0]][neighbour[1]] == 0:
                liberties.append(neighbour)
    return get_unique_list(liberties)

def find_dead_stones(player, board):
    dead_pieces = []
    for i in range(0, BOARD_SIZE):
        for j in range(0, BOARD_SIZE):
            if board[i][j] == player:
                if not does_liberty_exists(i, j, board, player):
                    dead_pieces.append((i, j))
    return dead_pieces

def clear_dead_stones(board, dead_pieces):
    for piece in dead_pieces:
        board[piece[0]][piece[1]] = 0
    return board

def adjacent_liberty_positions(i,j,board,player):
    liberties = []
    neighbors = get_adjacent_neighbours(i,j)
    for piece in neighbors:
        if board[piece[0]][piece[1]] == 0:
            liberties.append(piece)
    return get_unique_list(liberties)

def place_stone(i, j, board, player):
    board[i][j] = player
    return board

def total_score_heuristics(board, player):
    player_count = 0
    for i in range(0, BOARD_SIZE):
        for j in range(0, BOARD_SIZE):
            if board[i][j] == player:
                player_count = player_count + 1
    return player_count

def player_death_chances_heuristics(board, player):
    liberty_player_count = 0
    for i in range(0, BOARD_SIZE):
        for j in range(0, BOARD_SIZE):
            if board[i][j] == player:
                liberty = get_liberty_positions(i, j, board, player)
                if len(liberty) <= 1:
                    liberty_player_count = liberty_player_count + 1
    return liberty_player_count

def add_komi_value(player_count):
    return player_count + float(BOARD_SIZE/2)

def compute_heuristic(board, player, player1_total_dead, player2_total_dead):
    player1_count = total_score_heuristics(board, PLAYER_1)
    player2_count = total_score_heuristics(board, PLAYER_2)
    player1_death_chances = player_death_chances_heuristics(board, PLAYER_1)
    player2_death_chances = player_death_chances_heuristics(board, PLAYER_2)
    player2_count = add_komi_value(player2_count)
    if player == PLAYER_1:
        hueristic_value1_player1 = player1_count - player2_count
        hueristic_value2_player1 = player2_death_chances - player1_death_chances
        hueristic_value3_player1 = player2_total_dead*REWARD - player1_total_dead*PENALTY
        return hueristic_value1_player1 + hueristic_value2_player1 + hueristic_value3_player1
    else:
        hueristic_value1_player2 = player2_count - player1_count
        hueristic_value2_player2 = player1_death_chances - player2_death_chances
        hueristic_value3_player2 = player1_total_dead*REWARD - player2_total_dead*PENALTY
        return hueristic_value1_player2 + hueristic_value2_player2 + hueristic_value3_player2

def ko_rule_check(previous_board, current_board, updated_board):
    if updated_board != current_board and updated_board != previous_board:
        return True
    else:
        return False

def get_any_valid_move(player, previous_board, current_board):
    valid_moves = []
    for i in range(0, BOARD_SIZE):
        for j in range(0, BOARD_SIZE):
            if current_board[i][j] == 0:
                copied_board = deepcopy(current_board)
                copied_board = place_stone(i, j, copied_board, player)
                dead_pieces = find_dead_stones(3 - player, copied_board)
                copied_board = clear_dead_stones(copied_board, dead_pieces)
                if does_liberty_exists(i, j, copied_board, player):
                    if ko_rule_check(previous_board, current_board, copied_board):
                        valid_moves.append((i, j, dead_pieces))
    return sorted(valid_moves, key = lambda deadscore: deadscore[2],reverse = True)

def is_position_board_edge(row, col):
    if row == 0 or col == 0 or row == BOARD_SIZE-1 or col == BOARD_SIZE-1:
        return True
    else:
        return False

def get_best_of_valid_moves(player, previous_board, current_board, best_moves):
    best_valid_moves = []
    for move in list(best_moves):
        copied_board = deepcopy(current_board)
        copied_board = place_stone(move[0], move[1], copied_board, player)
        dead_pieces = find_dead_stones(3 - player, copied_board)
        copied_board = clear_dead_stones(copied_board, dead_pieces)
        if does_liberty_exists(move[0], move[1], copied_board, player):
            if ko_rule_check(previous_board, current_board, copied_board):
                best_valid_moves.append((move[0], move[1], dead_pieces))
    return best_valid_moves

def get_killer_moves(row, col, board, player):
    self_liberties = get_liberty_positions(row, col, board, player)
    killer_moves = []
    if len(self_liberties) == 1:
        killer_moves.extend(self_liberties)
        if is_position_board_edge(row, col):
            killer_positions = adjacent_liberty_positions(self_liberties[0][0], self_liberties[0][1], board, player)
            if killer_positions is not None and len(killer_positions) != 0:
                killer_moves.extend(killer_positions)
    return get_unique_list(killer_moves)

def best_moves(player, previous_board, current_board):
    best_moves = []
    best_valid_moves = []
    for i in range(0, BOARD_SIZE):
        for j in range(0, BOARD_SIZE):
            if current_board[i][j] == player:
                best_moves.extend(get_killer_moves(i, j, current_board, player))
            elif current_board[i][j] == 3-player:
                best_moves.extend(get_liberty_positions(i, j, current_board, 3-player))

    distinct_best_moves = get_unique_list(best_moves)
    if len(list(distinct_best_moves)) != 0:
        best_valid_moves = get_best_of_valid_moves(player, previous_board, current_board, distinct_best_moves)
        if len(best_valid_moves) != 0:
            return sorted(best_valid_moves, key = lambda deadscore: deadscore[2],reverse = True)
    return get_any_valid_move(player, previous_board, current_board)

def get_move(board,previous_board,player):
    score, actions = minimax(board,previous_board,player, 2, float("-inf"), float("inf"), 0, True)
    if actions is None or len(actions) == 0:
        return "PASS"
    else:
        return actions[0]

def minimax(board, previous_board, player, depth, alpha, beta, dead_pieces_length, isMaximizing):
    set_player_dead_pieces_count(player, dead_pieces_length)
    if depth == 0:
        value = compute_heuristic(board, player, PLAYER1_DEAD_PIECES_COUNT, PLAYER2_DEAD_PIECES_COUNT)
        return value, []

    if(isMaximizing):
        best_score = float("-inf")
        best_score_actions = []
        good_moves = best_moves(player, previous_board, board)
        if len(good_moves) == (BOARD_SIZE*BOARD_SIZE):
            return 20,BEST_START_POSITION
        for move in good_moves:
            copied_board = deepcopy(board)
            old_board = deepcopy(board)
            copied_board = place_stone(move[0], move[1], copied_board, player)
            old_board = place_stone(move[0], move[1], old_board, player)
            dead_pieces = find_dead_stones(3 - player, copied_board)
            copied_board = clear_dead_stones(copied_board, dead_pieces)
            score, actions = minimax(copied_board, board, 3-player, depth-1, alpha, beta, len(dead_pieces), False)
            if score > best_score:
                best_score = score
                best_score_actions = [move] + actions
            if best_score > beta:
                return best_score, best_score_actions
            alpha = max(best_score, alpha)
        return best_score, best_score_actions
    else:
        low_score = float("inf")
        low_score_actions = []
        good_moves = best_moves(player, previous_board, board)
        for move in good_moves:
            copied_board = deepcopy(board)
            old_board = deepcopy(board)
            copied_board = place_stone(move[0], move[1], copied_board, player)
            old_board = place_stone(move[0], move[1], old_board, player)
            dead_pieces = find_dead_stones(3 - player, copied_board)
            copied_board = clear_dead_stones(copied_board, dead_pieces)
            score, actions = minimax(copied_board, board, 3-player, depth-1, alpha, beta, len(dead_pieces), True)
            if score < low_score:
                low_score = score
                low_score_actions = [move] + actions
            if low_score < alpha:
                return low_score, low_score_actions
            if low_score < beta:
                alpha = low_score
        return low_score, low_score_actions

if __name__ == "__main__":
    player, previous_board, current_board = read_input("input.txt")
    actions = get_move(current_board, previous_board, player)
    write_output(actions)
