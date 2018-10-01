import unittest
import os
from src import DatasetBuilder
import random
import numpy as np
import pandas as pd


class TestShoppingSimulator(unittest.TestCase):
    TOL = 0.0000001  # Accepted level of error
    TEST_DIR = os.path.abspath('.')
    TEST_DIR = os.path.join(TEST_DIR, "test")
    def setUp(self):
        """ Sets up test environment. In practice you may have an array of
            test cases each with their own parameters possibly in a separate
            configuration file. This is a proof of concept.
        """
        # Load arguments
        self.args = dict()
        self.args["input_dir"] = os.path.join(TestShoppingSimulator.TEST_DIR, 'test_data', 'input')
        self.args["output_dir"] = os.path.join(TestShoppingSimulator.TEST_DIR, 'test_data', 'output')
        self.args["num_groups"] = 3
        self.args["num_users"] = 450
        self.args["num_items"] = 12
        self.args["group_distributions_file"] = 'user_group_distributions.csv'
        self.args["group_probabilities_file"] = 'user_group_probabilities.csv'
        self.args["num_trips"] = 18
        self.args["shelf_size"] = 6
        self.args["seed"] = 1234

        self.args = pd.Series(self.args)

        random.seed(self.args.seed)
        np.random.seed(self.args.seed)
        print("Test arguments loaded.")

    def test_shopping_simulator(self):
        """ Method to test the program main functionality.
            Given reference input and output files, it runs the dataset builder.
            Then, it compares the results with the reference files.
        """
        print("Starting dataset builder.")
        db = DatasetBuilder(self.args)
        db.generate_data_set(save=False)  # save=False to avoid writing over reference files
        true_user_utilities, data_set = db.get_results()

        # Read reference data from disc
        ref_user_util_path = os.path.join(self.args.output_dir, 'true_user_utilities.csv')
        ref_user_utilities = pd.read_csv(ref_user_util_path)
        ref_data_set_path = os.path.join(self.args.output_dir, 'simulated_data.csv')
        ref_data_set = pd.read_csv(ref_data_set_path)

        # Test for equality. Some precision is lost when writing to csv hence we need to have a tolerance.
        self.assertTrue(np.all(np.abs(true_user_utilities.values - ref_user_utilities.values) < TestShoppingSimulator.TOL))
        self.assertTrue(np.all(np.abs(data_set.values - ref_data_set.values) < TestShoppingSimulator.TOL))


if __name__ == '__main__':
    unittest.main()
