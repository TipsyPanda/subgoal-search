from queue import PriorityQueue
import random
import logging
import heapq
import random
import numpy as np
from supervised.rush import rush_solver_utils
from metric_logging import log_text

from solvers.core import Solver
from supervised.rubik.rubik_solver_utils import cube_to_string, make_RubikEnv
from policies import ConditionalPolicyRubik, VanillaPolicyRubik
from supervised.rush.heuristic_block import num_blocking_cars


N = 6
EMPTY_SPACE = '.'
ICE_CREAM_TRUCK = 'A'
START_ROW = 2
PLIES = {}

class SolverNode:
    def __init__(self, state, parent, depth, child_num, path, done):
        self.state = state
        self.parent = parent
        self.depth = depth
        self.child_num = child_num
        self.path = path
        self.done = done
        self.children = []
        self.hash = state

    def add_child(self, child):
        self.children.append(child)

    def set_value(self, value):
        self.value = value


class GeneralSolver(Solver):
    def __init__(self):
        self.core_env = make_RubikEnv()


class AStarSolverRush(GeneralSolver):
    def __init__(self,
                 goal_builder_class=None,
                 value_estimator_class=None,
                 max_tree_size=None,
                 max_tree_depth=None,
                 ):
        super().__init__()
        self.max_tree_size = max_tree_size
        self.max_tree_depth = max_tree_depth
        self.goal_builder_class = goal_builder_class
        self.value_estimator_class = value_estimator_class
        self.goal_builder = self.goal_builder_class()
        self.value_estimator = self.value_estimator_class()

    def construct_networks(self):

        self.value_estimator.construct_networks()
        self.goal_builder.construct_networks()

    def solve(self, input):
        PLIES = {}
        board_strings = input['board_string'] 
        additional_info= board_strings
        board_strings = rush_solver_utils.update_board_representation(board_strings)
        tree_metrics = {}
        root = []
        inter_goals = {}
        trajectory_actions = {}
        log_text('A* Solver run started', additional_info )
        root= "A*"
        board = convert_to_6x6_char_list(board_strings[0])
        path = a_star_solver(board)
        print('Solved length: {} (Optimal path length: {}), Number of nodes: {}'.format(path[2], input['opt_solve'], path[1]))
        tree_metrics = { 
                'method' :"A*",            
                'nodes' : path[1],
                'expanded_nodes': 0,
                'unexpanded_nodes': 0,
                'solve_length': path[2],
                'opt_solve' : input['opt_solve'],
                }
        #print(PLIES)
        #print('\n\n'.join(board_str(_) for _ in path))
        return (inter_goals, tree_metrics, root, trajectory_actions, additional_info)




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

def convert_to_6x6_char_list(board_strings):
    board = []

    for row in board_strings:
        board.append(list(row))

    return board