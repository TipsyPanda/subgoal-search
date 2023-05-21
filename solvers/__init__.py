import gin

from solvers import solver_sokoban
from solvers import bfs_solver_int
from solvers import bfs_solver_rubik
from solvers import bfs_solver_rush
from solvers import sub_solver_rush
from solvers import a_star_solver_rush


def configure_solver(goal_generator_class):
    return gin.external_configurable(
        goal_generator_class, module='solvers'
    )


BestFSSolverSokoban = configure_solver(solver_sokoban.BestFSSolverSokoban)
BestFSSolverINT = configure_solver(bfs_solver_int.BestFSSolverINT)
BestFSSolverRubik = configure_solver(bfs_solver_rubik.BestFSSolverRubik)
BfsSolverRush = configure_solver(bfs_solver_rush.BfsSolverRush)
SubSolverRush = configure_solver(sub_solver_rush.SubSolverRush)
AStarSolverRush = configure_solver(a_star_solver_rush.AStarSolverRush)
