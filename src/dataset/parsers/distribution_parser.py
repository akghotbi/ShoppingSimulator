import pandas as pd
import numpy as np


class DistributionParser:
    """ Reads the content of distribution files.
        Checks for common errors and catches cases which may cause numerical error.
    """
    def __init__(self, group_distributions_file, group_probabilities_file, num_items, num_groups):
        self.group_distributions = pd.read_csv(group_distributions_file)
        self.group_probabilities = pd.read_csv(group_probabilities_file)
        self.num_groups = num_groups
        if self.group_distributions.shape[0] != num_items*num_groups:
            raise ValueError('The group distribution file content is not aligned with num_items provided.')

        if self.group_probabilities.shape[0] != num_groups:
            raise ValueError('The group probabilities file content is not aligned with num_groups provided.')

        if sum(self.group_probabilities['probability']) != 1.0:
            raise ValueError('The group probabilities should add up to 1.0.')

        if len(self.group_distributions.group.unique()) != num_groups:
            raise ValueError('The number of distinct groups in group distribution file does not match num_groups.')
        self.group_probabilities = self.group_probabilities['probability'].values
        self.canonical_user_distributions = self.parse_group_distributions(num_items, num_groups)

    def parse_group_distributions(self, num_items, num_groups):
        """ Parses Gaussian distributions to makes sure
            - Dimensions match other commandline specs
            - The covariance matrices provided are positive definite

            Returns:
                canonical_user_distributions:   A dictionary with keys as group numbers.
                                                Values a list of two entities:
                                                    (a) Gaussian mean vector
                                                    (b) Gaussian covariance matrix
        """
        canonical_user_distributions = dict()
        for g in range(num_groups):
            idx = (self.group_distributions['group'] == (g+1)).values
            mu = self.group_distributions['mean'][idx].values
            if mu.size != num_items:
                raise ValueError('Dimension mismatch: Group mean of Gaussian for group {0:d}'.format(g))
            cov = self.group_distributions.iloc[:, 2:].loc[idx].values
            if cov.shape[0] != cov.shape[1]:
                raise ValueError('Dimension mismatch: Group cov of Gaussian for group {0:d}'.format(g))
            if not np.all(np.linalg.eigvals(cov) > 0):
                raise ValueError('Group cov of Gaussian for group {0:d} is not positive definite.'.format(g))
            canonical_user_distributions[g] = [mu, cov]
        return canonical_user_distributions

    def get_group_probabilities(self):
        return self.group_probabilities

    def get_group_distribution(self, group_index):
        """ Returns mean and cov for specified group """
        return self.canonical_user_distributions[group_index]

