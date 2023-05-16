import heapq

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

def board_str(board):
    return ''.join(''.join(row) for row in board)

def get_next_states(board):
    EMPTY_SPACE = '.'
    N = 6

    next_states = []
    for r in range(N):
        for c in range(N):
            char = board[r][c]
            if char != EMPTY_SPACE:
                # Check if the car is vertical or horizontal
                is_vertical = r < N-1 and board[r+1][c] == char

                # Find the extrema of the car
                min_r, max_r = r, r
                min_c, max_c = c, c
                while min_r - int(is_vertical) >= 0 and board[min_r - int(is_vertical)][min_c] == char:
                    min_r -= int(is_vertical)
                while max_r + int(is_vertical) < N and board[max_r + int(is_vertical)][max_c] == char:
                    max_r += int(is_vertical)
                while min_c - int(not is_vertical) >= 0 and board[min_r][min_c - int(not is_vertical)] == char:
                    min_c -= int(not is_vertical)
                while max_c + int(not is_vertical) < N and board[max_r][max_c + int(not is_vertical)] == char:
                    max_c += int(not is_vertical)

                # Try to move the car one space up or left
                if min_r - int(is_vertical) >= 0 and min_c - int(not is_vertical) >= 0 and board[min_r - int(is_vertical)][min_c - int(not is_vertical)] == EMPTY_SPACE:
                    next_state = [row.copy() for row in board]
                    next_state[min_r - int(is_vertical)][min_c - int(not is_vertical)] = char
                    if is_vertical:
                        next_state[max_r][max_c] = EMPTY_SPACE
                    else:
                        next_state[min_r][max_c] = EMPTY_SPACE
                    next_states.append(next_state)

                # Try to move the car one space down or right
                if max_r + int(is_vertical) < N and max_c + int(not is_vertical) < N and board[max_r + int(is_vertical)][max_c + int(not is_vertical)] == EMPTY_SPACE:
                    next_state = [row.copy() for row in board]
                    next_state[max_r + int(is_vertical)][max_c + int(not is_vertical)] = char
                    if is_vertical:
                        next_state[min_r][min_c] = EMPTY_SPACE
                    else:
                        next_state[min_r][min_c] = EMPTY_SPACE
                    next_states.append(next_state)

    return next_states

def get_next_states_2(board):
  EMPTY_SPACE = '.'
  N=6
  processed_chars_set = set([EMPTY_SPACE])
  next_states = []
  for r in range(N):
    for c in range(N):
      char = board[r][c]
      if char not in processed_chars_set:
        processed_chars_set.add(char)
        delta_r = 0
        delta_c = 0
        is_vertical = not char.isupper()
        if is_vertical:
          delta_r = 1
        else:
          delta_c = 1

        # Find the extrema
        min_r, max_r = r, r
        min_c, max_c = c, c
        while min_r - delta_r >= 0 and min_c - delta_c >= 0 and board[min_r - delta_r][min_c - delta_c] == char:
          min_r -= delta_r
          min_c -= delta_c

        while max_r + delta_r < N and max_c + delta_c < N and board[max_r + delta_r][max_c + delta_c] == char:
          max_r += delta_r
          max_c += delta_c

        if min_r - delta_r >= 0 and min_c - delta_c >= 0 and board[min_r - delta_r][min_c - delta_c] == EMPTY_SPACE:
          next_state = copy_board(board)
          next_state[min_r - delta_r][min_c - delta_c] = char
          next_state[max_r][max_c] = EMPTY_SPACE
          next_states.append(next_state)

        if max_r + delta_r < N and max_c + delta_c < N and board[max_r + delta_r][max_c + delta_c] == EMPTY_SPACE:
          next_state = copy_board(board)
          next_state[min_r][min_c] = EMPTY_SPACE
          next_state[max_r + delta_r][max_c + delta_c] = char
          next_states.append(next_state)

  return next_states

def copy_board(board):
  return [_[:] for _ in board]

def a_star_solver(board):
    # Define start state and goal test
    start = board
    def is_goal(board):
        return num_blocking_cars(board) == 0

    # Priority queue, each item will be a tuple (priority, depth, current_state)
    queue = [(num_blocking_cars(start), 0, start)]  # depth is 0 for start state
    visited = set()

    # Initialize visited count
    visited_count = 0

    while queue:
        (priority, depth, current) = heapq.heappop(queue)

        # If this node has been visited, skip
        if board_str(current) in visited:
            continue

        # If we have reached the goal, return
        if is_goal(current):
            return current, visited_count, depth  # Return the count and depth as well

        visited.add(board_str(current))

        # Increment visited count
        visited_count += 1

        # Generate next states and add them to the queue
        for next_state in get_next_states_2(current):
            if board_str(next_state) not in visited:
                estimated_cost_to_goal = num_blocking_cars(next_state)
                # the depth of next_state is current depth + 1
                heapq.heappush(queue, (estimated_cost_to_goal, depth + 1, next_state))

    return None, visited_count, None  # Return the count and depth even if no solution is found


# board_str = "..iBBB..ik..AAjk.lCCjDDlghEE.lghFF.."
# print(num_blocking_cars(board_str))  # Output: 1

board_list = [['.', '.', 'i', 'B', 'B', 'B'], ['.', '.', 'i', 'k', '.', '.'], ['A', 'A', 'j', 'k', '.', 'l'], ['C', 'C', 'j', 'D', 'D', 'l'], ['g', 'h', 'E', 'E', '.', 'l'], ['g', 'h', 'F', 'F', '.', '.']]
board_list = [['g', 'B', 'B', '.', 'l', '.'], ['g', 'h', 'i', '.', 'l', 'm'], ['g', 'h', 'i', 'A', 'A', 'm'], ['C', 'C', 'C', 'k', '.', 'm'], ['.', '.', 'j', 'k', 'D', 'D'], ['E', 'E', 'j', 'F', 'F', '.']]
print(num_blocking_cars(board_list))  # Output: 1
print(a_star_solver(board_list))



