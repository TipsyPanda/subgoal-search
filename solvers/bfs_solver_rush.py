from queue import PriorityQueue
import random
import logging

import random
import time
import numpy as np
from supervised.rush import rush_solver_utils
from metric_logging import log_text


from solvers.core import Solver
from supervised.rubik.rubik_solver_utils import cube_to_string, make_RubikEnv
from policies import ConditionalPolicyRubik, VanillaPolicyRubik



N = 6
EMPTY_SPACE = '.'
GOAL_CAR = 'A'
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


class BfsSolverRush(GeneralSolver):
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
        # log_text('BFS Solver run started', additional_info )
        board = convert_to_6x6_char_list(board_strings[0])
        solve_time_start = time.time()
        path = bfs_solve(board)
        solve_time = time.time() - solve_time_start
        root= "BFS"
        # print('Solved length: {} (Optimal path length: {}), Number of nodes: {} , Time: {}'.format(len(path[0]), input['opt_solve'],path[2],solve_time ))
        tree_metrics = {
          'method' :"BFS",
          'board' : input['board_string'],
          'nodes' : path[2],
          'solve_length': len(path[0]),
          'opt_solve' : input['opt_solve'],
          'solve_time' : solve_time,

          }
        #print_path(path)
        return (inter_goals, tree_metrics, root, trajectory_actions, additional_info)


def board_str(board):
  return '\n'.join(''.join(_) for _ in board)


def copy_board(board):
  return [_[:] for _ in board]


def is_solved(board):
  # Find any obstacles between the goal car and the right edge.
  for i in range(N - 1, -1, -1):
    char_i = board[START_ROW][i]
    if char_i == EMPTY_SPACE:
      continue
    elif char_i == GOAL_CAR:
      return True
    else:
      return False

  return True

#to be extended with subgoal logic
def get_next_states(board):
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



def bfs_solve(board):
  queue = [(0, [board])]
  board_hash_set = set()
  nodes_expanded = 0  

  while queue:
    ply, path = queue.pop(0)
    if ply not in PLIES:
      PLIES[ply] = 1
    else:
      PLIES[ply] += 1
        
    nodes_expanded += 1 
    if is_solved(path[-1]):
      return path,len(path),nodes_expanded

    for next_state in get_next_states(path[-1]):
      if board_str(next_state) not in board_hash_set:
        board_hash_set.add(board_str(next_state))
        queue.append((ply + 1, path + [next_state]))

  return [],len(board_hash_set), nodes_expanded

def get_board2():

    board_data = [
        "..iBBB",
        "..ik..",
        "AAjk.l",
        "CCjDDl",
        "ghEE.l",
        "ghFF.."
    ]

    board = [[char for char in row] for row in board_data]
    print(board)
    return board


def convert_to_6x6_char_list(board_strings):
    board = []

    for row in board_strings:
        board.append(list(row))

    return board

def print_path(path):
    for i, board in enumerate(path[0]):
        print(f"Step {i}:")
        for row in board:
            print(''.join(row))
        print("\n")


