def num_blocking_cars(board):
    EMPTY_SPACE = '.'
    GOAL_CAR = 'A'
    N = 6
    
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

# board_str = "..iBBB..ik..AAjk.lCCjDDlghEE.lghFF.."
# print(num_blocking_cars(board_str))  # Output: 1

# board_list = [['.', '.', 'i', 'B', 'B', 'B'], ['.', '.', 'i', 'k', '.', '.'], ['A', 'A', 'j', 'k', '.', 'l'], ['C', 'C', 'j', 'D', 'D', 'l'], ['g', 'h', 'E', 'E', '.', 'l'], ['g', 'h', 'F', 'F', '.', '.']]
# board_list = [['g', 'B', 'B', '.', 'l', '.'], ['g', 'h', 'i', '.', 'l', 'm'], ['g', 'h', 'i', 'A', 'A', 'm'], ['C', 'C', 'C', 'k', '.', 'm'], ['.', '.', 'j', 'k', 'D', 'D'], ['E', 'E', 'j', 'F', 'F', '.']]
# print(num_blocking_cars(board_list))  # Output: 1
# print(a_star_solver(board_list))



