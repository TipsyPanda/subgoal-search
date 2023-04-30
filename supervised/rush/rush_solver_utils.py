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
    return rushStartStates

def read_file(filename):
    data = []
    with open(filename, 'r') as file:
        for line in file:
            split_line = line.strip().split(' ')
            opt_solve = int(split_line[0])
            board_string = split_line[1]
            size = int(split_line[2])

            data.append({
                'opt_solve': opt_solve,
                'board_string': board_string,
                'size': size
            })

    return data

def update_board_representation(board_strings):
    N = 6
    if isinstance(board_strings, str):  # Check if input is a single string
        board_strings = [board_strings]  # Convert it into a list with a single element

    def process_board_string(board_string):
        updated_board = []

        for i in range(0, len(board_string), N):
            row = board_string[i:i + N]
            updated_board.append(list(row))

        for r in range(N):
            for c in range(N):
                char = updated_board[r][c]
                if char != '.':
                    vertical_count = 1
                    horizontal_count = 1
                    
                    # Check for vertical cars
                    while r + vertical_count < N and updated_board[r + vertical_count][c] == char:
                        vertical_count += 1
                    
                    # Check for horizontal cars
                    while c + horizontal_count < N and updated_board[r][c + horizontal_count] == char:
                        horizontal_count += 1

                    # Update the character based on car orientation and length
                    if vertical_count > 1:
                        for i in range(vertical_count):
                            updated_board[r + i][c] = char.lower()
                    elif horizontal_count > 1:
                        for i in range(horizontal_count):
                            updated_board[r][c + i] = char.upper()

        updated_board_rows = [''.join(row) for row in updated_board]
        return updated_board_rows

    all_updated_boards = [process_board_string(board_string) for board_string in board_strings]
    return all_updated_boards




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