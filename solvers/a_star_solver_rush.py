from queue import PriorityQueue
import random
import logging
import heapq
import random
import time
import numpy as np
from supervised.rush import rush_solver_utils
from metric_logging import log_text

from solvers.core import Solver
from supervised.rubik.rubik_solver_utils import cube_to_string, make_RubikEnv
from policies import ConditionalPolicyRubik, VanillaPolicyRubik
from supervised.rush.heuristic_block import num_blocking_cars, num_blocking_cars_simple


N = 6
EMPTY_SPACE = '.'
ICE_CREAM_TRUCK = 'A'
START_ROW = 2
PLIES = {}

class SolverNode:
    def __init__(self, state, parent,move, depth, child_num, path, done):
        self.state = state
        self.parent = parent
        self.depth = depth
        self.child_num = child_num
        self.path = path
        self.done = done
        self.children = []
        self.hash = state
        self.move = move  # The move that led to this state

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
        # log_text('A* Solver run started', additional_info )
        root= "A*"
        board = convert_to_6x6_char_list(board_strings[0])
        solve_time_start = time.time()
        path = a_star_solver(board)
        solve_time = time.time() - solve_time_start
        # print('Solved length: {} (Optimal path length: {}), Number of nodes: {}, Time: {}'.format(path[2], input['opt_solve'], path[1],solve_time ))
        tree_metrics = { 
                'method' :"A*_zero",     
                'board' : input['board_string'] ,       
                'nodes' : path[1],
                'solve_length': path[2],
                'opt_solve' : input['opt_solve'],
                'solve_time' : solve_time,
                }
        return (inter_goals, tree_metrics, root, trajectory_actions, additional_info)




def board_str(board):
    return ''.join(''.join(row) for row in board)


def get_next_states(board):
    EMPTY_SPACE = '.'
    N = 6
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
                    # Include move with next_state
                    move = (char, (max_r, max_c), (min_r - delta_r, min_c - delta_c))
                    next_states.append((next_state, move))

                if max_r + delta_r < N and max_c + delta_c < N and board[max_r + delta_r][max_c + delta_c] == EMPTY_SPACE:
                    next_state = copy_board(board)
                    next_state[min_r][min_c] = EMPTY_SPACE
                    next_state[max_r + delta_r][max_c + delta_c] = char
                    # Include move with next_state
                    move = (char, (min_r, min_c), (max_r + delta_r, max_c + delta_c))
                    next_states.append((next_state, move))

    return next_states


def copy_board(board):
  return [_[:] for _ in board]

def a_star_solver(board):
    start = board

    def is_goal(board):
        return num_blocking_cars_simple(board) == 0

    queue = [(num_blocking_cars(start), 0, start)]  # priority queue
    visited = set()
    parents = {}  # New dictionary to record the parent of each state and the move that led to it
    visited_count = 0

    while queue:
        (priority, depth, current) = heapq.heappop(queue)

        if board_str(current) in visited:
            continue

        if is_goal(current):
            path, moves = backtrack_path(current, parents)  # Use the parents dictionary to backtrack the solution path
            # print_path(path)
            return path, visited_count, depth

        visited.add(board_str(current))
        visited_count += 1

        for next_state, move in get_next_states(current):
            if board_str(next_state) not in visited:
                parents[board_str(next_state)] = (current, move)  # Record the parent state and the move that led to next_state
                estimated_cost_to_goal = num_blocking_cars(next_state)
                heapq.heappush(queue, (estimated_cost_to_goal, depth + 1, next_state))

    return None, visited_count, None


def convert_to_6x6_char_list(board_strings):
    board = []

    for row in board_strings:
        board.append(list(row))

    return board

def backtrack_path(goal_state, parents):
    path = []
    moves = []
    current_state = goal_state
    while current_state is not None:
        path.append(current_state)
        if board_str(current_state) in parents:
            current_state, move = parents[board_str(current_state)]
            moves.append(move)
        else:
            current_state = None
    return path[::-1], moves[::-1]

def print_path(path):
    for i, board in enumerate(path):
        print(f"Step {i}:")
        for row in board:
            print(' '.join(row))
        print("\n")
