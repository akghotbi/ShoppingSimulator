import os
import sys
import numpy as np
import pandas as pd
from src.dataset.doe import doe_builder
from src.dataset.user import user_builder
from src.dataset.parsers import distribution_parser


class DatasetBuilder:
    """ The main engine of simulation.
        After parsing the command line parameters and checking for possible errors,
        doe and user generator objects are instantiated to mimic real shopping behavior.
    """

    NUM_NON_DOE_DATASET_COLUMNS = 3
    NUM_USER_UTILITY_COLUMNS = 2

    def __init__(self, args):
        print("Initializing data set builder... Checking arguments...")
        self.input_dir = args.input_dir
        self.output_dir = args.output_dir
        self.num_groups = int(args.num_groups)
        self.group_distributions_file = args.group_distributions_file
        self.group_probabilities_file = args.group_probabilities_file
        self.num_users = int(args.num_users)
        self.num_items = int(args.num_items)
        self.num_trips = int(args.num_trips)
        self.shelf_size = int(args.shelf_size)
        self.inspect_arguments(args)
        print("Checking arguments done.")

        print("Reading canonical distribution data and unpacking them...")
        self.group_distributions = distribution_parser.DistributionParser(self.group_distributions_file,
                                                                          self.group_probabilities_file,
                                                                          self.num_items, self.num_groups)

        print("Instantiating DoE builder")
        self.shopping_env_simulator = doe_builder.DoEBuilder(self.num_items,
                                                             self.num_trips, self.shelf_size)
        self.true_user_utilities = None
        self.user_groups = None
        self.data_set = None
        print("Done with initializing dataset builder.")

    def inspect_arguments(self, args):
        """ Inspects arguments for common errors. Raises appropriate errors accordingly.
            :param args: The argument object processed by argparse.
        """
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        if not os.path.exists(self.input_dir):
            raise ValueError('Specified input directory could not be found.')

        self.group_distributions_file = os.path.join(self.input_dir, self.group_distributions_file)
        if not os.path.exists(self.group_distributions_file):
            raise ValueError('Specified groups distribution file could not be found in input directory.')

        self.group_probabilities_file = os.path.join(self.input_dir, self.group_probabilities_file)
        if not os.path.exists(self.group_probabilities_file):
            raise ValueError('Specified groups probabilities file could not be found in input directory.')

    def draw_user_groups(self):
        """ Draws shopper memberships according to group probabilities file content.
            Assigns each shopper to a canonical group of like-minded shoppers.
        """
        group_prob = self.group_distributions.get_group_probabilities()
        self.user_groups = np.random.choice(a=self.num_groups, size=self.num_users, p=group_prob)

    def generate_data_set(self, save=True):
        """ Draws user preferences from associated Gaussian.
            Simulates DoE and shopper choices in one place.
            Produces user utilities and data set.
        """

        print("Draw user memberships")
        self.draw_user_groups()

        print("Initialize user utilities and dataset structure")
        self.true_user_utilities = pd.DataFrame(data=np.zeros([self.num_users,
                                                               self.num_items +
                                                               DatasetBuilder.NUM_USER_UTILITY_COLUMNS]),
                                                columns=["user_id", "user_group"] +
                                                        ['item{0:03d}'.format(i) for i in range(self.num_items)])

        self.data_set = pd.DataFrame(data=np.zeros([self.num_users * self.num_trips,
                                                    (DatasetBuilder.NUM_NON_DOE_DATASET_COLUMNS + self.num_items)]),
                                     columns=["user_id", "trip", "choice"] +
                                             ["item{0:03}".format(i) for i in range(self.num_items)])

        print("Dataset generation started...")
        row_index = 0
        for iu in range(self.num_users):
            if ((iu+1) % 50 == 0):
                sys.stdout.write("\r{0:d}/{1:d}".format(iu+1, self.num_users))
                sys.stdout.flush()

            # Generate a new user and draw its item utilities
            new_user = user_builder.UserBuilder(self.group_distributions.get_group_distribution(self.user_groups[iu]),
                                                iu,
                                                self.user_groups[iu])
            self.true_user_utilities.iloc[iu, 0] = new_user.user_id
            self.true_user_utilities.iloc[iu, 1] = new_user.user_group
            self.true_user_utilities.iloc[iu, DatasetBuilder.NUM_USER_UTILITY_COLUMNS:] = new_user.get_utilities()

            # Make sure DoE generator is reset before first shopping trip
            self.shopping_env_simulator.reset()

            # Simulate shopping trips for user
            for it in range(self.num_trips):
                idx, x = self.shopping_env_simulator.next_shelf()
                self.data_set.iloc[row_index, :DatasetBuilder.NUM_NON_DOE_DATASET_COLUMNS] = new_user.choose_from_items(idx)
                self.data_set.iloc[row_index, DatasetBuilder.NUM_NON_DOE_DATASET_COLUMNS:] = x
                row_index += 1
        print("")
        print("Done generating dataset.")
        if(save):
            self.save_results()

    def save_results(self):
        print("Writing user utilities and full dataset to disk.")
        self.true_user_utilities.to_csv(os.path.join(self.output_dir, 'true_user_utilities.csv'), index=False)
        self.data_set.to_csv(os.path.join(self.output_dir, 'simulated_data.csv'), index=False)

    def get_results(self):
        return self.true_user_utilities, self.data_set

    def generate_reports(self):
        """ Verifies the simulation first for users and then for the design.
            Note that doe is simulated with a very simple sampling scheme.
            Balance and orthogonality is not directly controlled here.
        """
        print("Generating reports.")
        # Input user memberships and utilities
        input_mean_util = dict()
        for g in range(self.num_groups):
            input_mean_util[g] = self.group_distributions.get_group_distribution(g)[0]
            input_mean_util[g] = input_mean_util[g]-input_mean_util[g][self.num_items-1]
        input_mean_util = pd.DataFrame.from_dict(data=input_mean_util, orient='index')
        input_mean_util.columns = ["mean_input_util_item{0:03d}".format(i) for i in range(self.num_items)]
        input_mean_util.reset_index(inplace=True, drop=True)

        input_memb_prob = self.group_distributions.get_group_probabilities()
        input_memb_prob = pd.DataFrame(data=input_memb_prob, columns=['input_memb_prob'])
        input_memb_prob.reset_index(inplace=True, drop=True)

        # Drawn user membership probabilities
        drawn_memb_prob = self.true_user_utilities.groupby(['user_group'])[['user_group']].count() / self.num_users
        drawn_memb_prob.rename(columns={'user_group': 'sim_memb_prob'}, inplace=True)
        drawn_memb_prob.reset_index(inplace=True, drop=True)

        # Drawn user utilities (mean)
        drawn_mean_util = self.true_user_utilities.groupby(['user_group']).mean()
        drawn_mean_util.drop(labels=['user_id'], axis=1, inplace=True)
        drawn_mean_util.columns = ["mean_sim_util_item{0:03d}".format(i) for i in range(self.num_items)]
        drawn_mean_util.reset_index(inplace=True, drop=True)

        user_summary = pd.concat(objs=[input_memb_prob, drawn_memb_prob, input_mean_util, drawn_mean_util], axis=1)
        user_summary.to_csv(os.path.join(self.output_dir, 'drawn_users_summary.csv'), index=False)

        # Checking design balance per user
        balance_per_user = self.data_set.groupby(['user_id']).sum()/(self.num_trips*self.shelf_size/self.num_items)
        balance_per_user.drop(labels=['trip', 'choice'], axis=1, inplace=True)
        balance_per_user.reset_index(inplace=True)
        balance_per_user.to_csv(os.path.join(self.output_dir, 'item_balance_per_user.csv'), index=False)

        print("Done with generating reports.")




