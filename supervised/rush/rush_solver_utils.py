from supervised.rush import gen_rush_data
from supervised.rush.gen_rush_data import make_env_Rush

filename = '/home/yannick_schmid/subgoal-search/subgoal-search-resources/rush/rush_all.txt'

def cube_to_string(cube):
    return gen_rush_data.BOS_LEXEME + gen_rush_data.cube_bin_to_str(cube) + gen_rush_data.EOS_LEXEME


def make_RushEnv():
    return make_env_Rush(step_limit=1e10, shuffles=100, obs_type='basic')


def generate_problems_rush(n_problems=None):
    rushStartStates = read_file(filename, n_problems)
    return rushStartStates

def read_file(filename, max_problems=None):
    data = []
    with open(filename, 'r') as file:
        for line_num, line in enumerate(file):
            # Stop reading once we have enough problems
            if max_problems is not None and line_num >= max_problems:
                break
            
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



def rush_hour_heuristic(board_string):
    N = 6
    target_car = 'A'
    exit_column = 5

    # Convert the board_string to a 6x6 board
    board = []
    for i in range(0, len(board_string), N):
        row = board_string[i:i + N]
        board.append(list(row))

    # The target car is always in row index 2 and has a horizontal orientation
    target_car_row = 2
    target_car_col = board[target_car_row].index(target_car)

    # Function to find the blocking cars
    def count_blocking_cars(car_row, car_col):
        count = 0

        for c in range(car_col + 1, N):
            if board[car_row][c] != '.':
                count += 1

        return count

    # Count the cars blocking the target car
    blocking_cars_count = count_blocking_cars(target_car_row, target_car_col + 1)

    return blocking_cars_count

# Test with a sample board_string
board_string = 'GBB.L.GHI.LMGHIAAMCCCK.M..JKDDEEJFF.'
print(rush_hour_heuristic(board_string))
