import logging
import csv

def log_tree_metrics(tree_metrics):
    logger = logging.getLogger(__name__)
    logger.info('Tree metrics:')
    logger.info('Nodes: %s', tree_metrics['nodes'])
    logger.info('Expanded nodes: %s', tree_metrics['expanded_nodes'])
    logger.info('Unexpanded nodes: %s', tree_metrics['unexpanded_nodes'])
    logger.info('Solution length: %s', tree_metrics['solve_length'])
    logger.info('Optimal solution: %s', tree_metrics['opt_solve'])

def log_tree_metrics_to_csv(results, filename, overwrite=True):
    # Extracting the tree_metrics dictionary from each result in results
    tree_metrics_list = [result['tree_metrics'] for result in results]

    mode = 'w' if overwrite else 'a'  # Choose file mode based on overwrite flag
    with open(filename, mode, newline='') as csvfile:
        fieldnames = tree_metrics_list[0].keys()  # Assume that all dictionaries have the same structure
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Only write the header if the file is empty or we're overwriting
        if overwrite or csvfile.tell() == 0:
            writer.writeheader()

        # Write each dictionary in tree_metrics_list as a row in the CSV
        for tree_metrics in tree_metrics_list:
            writer.writerow(tree_metrics)
