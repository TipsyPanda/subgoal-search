import logging


def log_tree_metrics(tree_metrics):
    logger = logging.getLogger(__name__)
    logger.info('Tree metrics:')
    logger.info('Nodes: %s', tree_metrics['nodes'])
    logger.info('Expanded nodes: %s', tree_metrics['expanded_nodes'])
    logger.info('Unexpanded nodes: %s', tree_metrics['unexpanded_nodes'])
    logger.info('Solution length: %s', tree_metrics['solve_length'])
    logger.info('Optimal solution: %s', tree_metrics['opt_solve'])