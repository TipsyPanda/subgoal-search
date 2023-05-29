EMPTY_SPACE = '.'
GOAL_CAR = 'A'
N = 6
HEURISTICS = 'ZERO'


def num_blocking_cars(board, heuristics=None):
    # If a specific heuristic is not provided for this call, use the global value
    if heuristics is None:
        heuristics = HEURISTICS

    if heuristics == 'ZERO':
        return num_blocking_cars_zero(board)
    elif heuristics == 'SIMPLE':
        return num_blocking_cars_simple(board)
    elif heuristics == 'ADVANCED':
        return num_blocking_cars_advanced(board)

def num_blocking_cars_zero(board):
    return 1

def num_blocking_cars_simple(board):
  
    # If the input is a string, convert it into a 2D list
    if isinstance(board, str):
        board = [list(board[i*N:(i+1)*N]) for i in range(N)]

    # Find the row and column of the goal car
    for i in range(N):
        for j in range(N):
            if board[i][j] == GOAL_CAR:
                goal_row = i
                goal_col = j
                break

    # Count the number of cars blocking the goal car from exiting
    num_blocking = 0
    for j in range(goal_col+2, N):
        if board[goal_row][j] != EMPTY_SPACE:
            num_blocking += 1
    
    return num_blocking


def num_blocking_cars_advanced(board):

    # If the input is a string, convert it into a 2D list
    if isinstance(board, str):
        board = [list(board[i*N:(i+1)*N]) for i in range(N)]
    
    # Print the board
    # print("Board:")
    # for row in board:
    #     print(row)

    # Find the row and column of the goal car
    for i in range(N):
        for j in range(N):
            if board[i][j] == GOAL_CAR:
                goal_row = i
                goal_col = j
                break

    # Count the number of cars blocking the goal car from exiting (Type 1)
    type_1_blocking = 0
    type_1_blocking_cars = []
    for j in range(goal_col+2, N):
        if board[goal_row][j] != EMPTY_SPACE:
            type_1_blocking += 1
            type_1_blocking_cars.append(board[goal_row][j])
            
    # print("\nType 1 Blocking Cars:", type_1_blocking_cars)

    # Count the number of cars blocking the first type cars from moving (Type 2)
    type_2_blocking = []
    for type_1_car in type_1_blocking_cars:
        for i in range(N):
            for j in range(N):
                if board[i][j] == type_1_car:
                    # Check the cars above and below if the blocking car is vertical
                        for k in range(N):
                            # Check the cars above if we're not on the first row
                            if i > 0 and board[k][j] != EMPTY_SPACE and board[k][j] != GOAL_CAR and board[k][j] != type_1_car and board[k][j] not in type_2_blocking:
                                type_2_blocking.append(board[k][j])
                            # Check the cars below if we're not on the last row
                            if i < N - 1 and board[k][j] != EMPTY_SPACE and board[k][j] != GOAL_CAR and board[k][j] != type_1_car and board[k][j] not in type_2_blocking:
                                type_2_blocking.append(board[k][j])

                            
    # print("\nType 2 Blocking Cars:", type_2_blocking)


    
    return type_1_blocking + len(type_2_blocking)



# board_str = "..iBBB..ik..AAjk.lCCjDDlghEE.lghFF.."
# print(num_blocking_cars(board_str))  # Output: 1

# board_list = [['.', '.', 'i', 'B', 'B', 'B'], ['.', '.', 'i', 'k', '.', '.'], ['A', 'A', 'j', 'k', '.', 'l'], ['C', 'C', 'j', 'D', 'D', 'l'], ['g', 'h', 'E', 'E', '.', 'l'], ['g', 'h', 'F', 'F', '.', '.']]
# # board_list = [['g', 'B', 'B', '.', 'l', '.'], ['g', 'h', 'i', '.', 'l', 'm'], ['g', 'h', 'i', 'A', 'A', 'm'], ['C', 'C', 'C', 'k', '.', 'm'], ['.', '.', 'j', 'k', 'D', 'D'], ['E', 'E', 'j', 'F', 'F', '.']]
# # print(num_blocking_cars(board_list))  # Output: 1
# # print(a_star_solver(board_list))
# print(num_blocking_cars_advanced(board_list))



