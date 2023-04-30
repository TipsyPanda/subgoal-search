import copy
import random
import sys

import gin
import gym

import numpy as np




solver_type = 'Random'  # Kociemba | Beginner | Random
observation_type = 'basic'  # basic | cubelet

if observation_type == 'basic':
    observation_shape = (54, 6)
else:
    observation_shape = (20, 24)


@gin.configurable
def n_random_moves(value=gin.REQUIRED):
    return value

@gin.configurable
def subgoal_skipped_steps(value=1):
    return value


def make_env_Rush(**kwargs):
    id = ("Rush-" + str(kwargs) + "-v0").translate(str.maketrans('', '', " {}'<>()_:"))
    id = id.replace(',', '-')

    try:
        gym.envs.register(id=id, entry_point='gym_rush.envs:RushEnv', kwargs=kwargs)
        print("Registered environment with id = " + id)
    except gym.error.Error:
        print("Environment with id = " + id + " already registered. Continuing with that environment.")

    env = gym.make(id)
    obs = env.reset()
    return env
