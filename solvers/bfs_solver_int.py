from queue import PriorityQueue
import random

import numpy as np

from envs import Sokoban
from envs.int.theorem_prover_env import TheoremProverEnv
from goal_builders.int.goal_builder_int import GoalBuilderINT
from solvers.core import Solver
from utils.utils_sokoban import get_field_index_from_name, HashableNumpyArray
from value_estimators.int.value_estimator_int import TrivialValueEstimatorINT
from third_party.INT.visualization.seq_parse import logic_statement_to_seq_string


class SolverNode:
    def __init__(self, state, parent, depth, child_num, path, done):
        self.state = state
        self.parent = parent
        self.depth = depth
        self.child_num = child_num
        self.path = path
        self.done = done
        self.children = []
        self.hash = logic_statement_to_seq_string(state['observation']['objectives'][0])

    def add_child(self, child):
        self.children.append(child)

    def set_value(self, value):
        self.value = value

class GeneralSolver(Solver):
    def __init__(self):
        self.core_env = TheoremProverEnv()

class BestFSSolverINT(GeneralSolver):
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
        self.goal_builder =  self.goal_builder_class()
        self.value_estimator = self.value_estimator_class()

    def construct_networks(self):

        self.value_estimator.construct_networks()
        self.goal_builder.construct_networks()

    def reset_counter(self):
        self.value_estimator.reset_counter()
        self.goal_builder.reset_counter()

    def read_counter(self):
        counters = {}
        counters.update(self.goal_builder.read_counter())
        counters.update(self.value_estimator.read_counter())
        return counters

    def solve(self, input):
        self.reset_counter()

        assert self.value_estimator is not None, 'you must load value estimator'
        solved = False
        root = SolverNode(input, None, 0, 0, [], False)
        nodes_queue = PriorityQueue()
        # To prevent situations where two exactly same states (thus with the same value),
        # cannot be compared, we add another dimension
        # with random number which are being compared in these rare situations.
        root_value = self.value_estimator.evaluate([root.state])[0]
        root.set_value(root_value)
        nodes_queue.put((-root_value, random.random(), root))
        solution = []
        tree_size = 1
        expanded_nodes = 0
        all_goals_created = 0
        tree_depth = 0
        total_path_between_goals = 0
        seen_hashed_states = {root.hash}

        while True:
            if nodes_queue.empty():
                finished_cause = 'Finished cause queue is empty'
                break
            if tree_size >= self.max_tree_size:
                finished_cause = 'Finished cause tree too big'
                break
            if solved:
                finished_cause =  'Finished cause solved'
                break

            #pop node from queue to expand
            curr_val, _, current_node = nodes_queue.get()
            # print(f'val = {curr_val} | {logic_statement_to_seq_string(current_node.state["observation"]["objectives"][0])}')
            expanded_nodes += 1

            # print(logic_statement_to_seq_string(current_node.state['observation']['objectives'][0]))

            if current_node.depth < self.max_tree_depth:
                goals = self.goal_builder.build_goals(current_node.state)
                # look for solution
                for goal in goals:
                    if goal.done:
                        new_node = SolverNode(goal.subgoal_state, current_node, current_node.depth + 1, 0,
                                   goal.actions, True)
                        solution.append(new_node)
                        solved = True
                        tree_size += 1
                        expanded_nodes += 1
                        break


                all_goals_created += len(goals)

                created_new = 0
                subgoal_values = []
                if len(goals) > 0:
                    subgoal_values = self.value_estimator.evaluate([goal.subgoal_state for goal in goals])

                for child_num, goal_proposition in enumerate(goals):
                    current_goal_state = goal_proposition.subgoal_state
                    current_path = goal_proposition.actions
                    current_goal_state_hash = logic_statement_to_seq_string(current_goal_state['observation']['objectives'][0])
                    total_path_between_goals += len(current_path)

                    if current_goal_state_hash not in seen_hashed_states:
                        created_new += 1
                        seen_hashed_states.add(current_goal_state_hash)
                        new_node = SolverNode(current_goal_state, current_node, current_node.depth + 1, child_num, current_path, False)
                        current_node.add_child(new_node)
                        tree_depth = max(tree_depth, new_node.depth)
                        node_val = subgoal_values[child_num]
                        new_node.set_value(node_val)
                        nodes_queue.put((-node_val, random.random(), new_node))
                        tree_size += 1


        tree_metrics = {'nodes' : tree_size,
                        'expanded_nodes': expanded_nodes,
                        'unexpanded_nodes': tree_size - expanded_nodes,
                        'max_depth' : tree_depth,
                        'avg_n_goals': all_goals_created/expanded_nodes if expanded_nodes > 0 else 0,
                        'avg_dist_between_goals' : total_path_between_goals/all_goals_created
                        if all_goals_created > 0 else 0
                        }

        additional_info = {
            'finished_cause': finished_cause,
            'predictions':  self.read_counter(),
        }
        if solved:
            node = solution[0]
            while node.parent is not None:
                solution.append(node.parent)
                node = node.parent

            trajectory_actions = []
            for inter_goal in solution:
                trajectory_actions = list(inter_goal.path) + trajectory_actions

            inter_goals = [node for node in reversed(solution)]
            return (inter_goals, tree_metrics, root, trajectory_actions, additional_info)
        else:
            return (None, tree_metrics, root, None, additional_info)

