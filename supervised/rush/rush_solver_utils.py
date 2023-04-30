from supervised.rush import gen_rush_data
from supervised.rush.gen_rush_data import make_env_Rush

filename = '/home/yannick_schmid/subgoal-search/subgoal-search-resources/rush/rush.txt'

def cube_to_string(cube):
    return gen_rush_data.BOS_LEXEME + gen_rush_data.cube_bin_to_str(cube) + gen_rush_data.EOS_LEXEME


def make_RushEnv():
    return make_env_Rush(step_limit=1e10, shuffles=100, obs_type='basic')


def generate_problems_rush(n_problems):
    problems = []
    rushStartStates = read_file(filename)
    board_strings = [item['board_string'] for item in rushStartStates]
    board_strings = update_board_representation(board_strings)

    return board_strings

def read_file(filename):
    data = []
    with open(filename, 'r') as file:
        for line in file:
            split_line = line.strip().split(' ')
            step_count = int(split_line[0])
            board_string = split_line[1]
            score = int(split_line[2])

            data.append({
                'step_count': step_count,
                'board_string': board_string,
                'score': score
            })

    return data

def update_board_representation(board_string):
    N = 6
    updated_board = []

    for i in range(0, len(board_string), N):
        row = board_string[i:i + N]
        updated_board.append(list(row))

    for r in range(N):
        for c in range(N):
            char = updated_board[r][c]
            if char != '.':
                if r < N - 1 and updated_board[r + 1][c] == char:
                    updated_board[r][c] = char.lower()  # Vertical car
                else:
                    updated_board[r][c] = char.upper()  # Horizontal car

    updated_board_string = ''.join(''.join(row) for row in updated_board)
    return updated_board_string


#TOKENS, MOVE_TOKENS, COL_TO_ID, MOVE_TOKEN_TO_ID = gen_rush_data.policy_encoding()


def decode_action(raw_action):
    if len(raw_action) < 3:
        # print('Generated invalid move:', raw_action)
        return None

    move = raw_action[2]

    if move not in MOVE_TOKEN_TO_ID:
        # print('Generated invalid move:', raw_action)
        return None

    return MOVE_TOKEN_TO_ID[move]

read_file(filename)