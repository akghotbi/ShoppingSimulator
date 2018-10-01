import argparse
import random
import numpy as np
from src.dataset import dataset_builder


def main():
    """ This is the main function to run.
        The assumption is when a shopper goes to a store to buy a product, he/she will be presented with a
        random assortment of products on an isle shelf. After inspection, the a product of choice is put in
        the shopping basket.

        This program aims at simulating this shopping behavior by simultaneously generating product assortments
        and shopper choices. To make things interesting we assume there are groups of like minded buyers. Given
        the group each shopper's propensity to choose a product is a random sample from a group specific gaussian
        distribution.

        Detailed description of commandline arguments:
        -i:     Input directory
        -o:     Output directory
        -ng:    Number of canonical groups of like minded shoppers
        -gdf:   csv file name in input dir including the group specific Gaussian distributions
        -gpf:   csv file name in input dir including membership probability for each group
        -nu:    Number of users to be simulated
        -ni:    Number of total items in the category
        -nt:    Number of shopping trips per user
        -ss:    The shelf size at store. In each trip, a random number of items are selected and
                will be available on store shelf.
        -se:    Seed for reproducibility

        Example run:
        python __main__.py
        -i <input_dir>
        -o <output_dir>
        -ng 3
        -gdf user_group_distributions.csv
        -gpf user_group_probabilities.csv
        -nu 450 -ni 12 -nt 18 -ss 6

        """
    print("Reading and parsing arguments.")
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_dir', help='Input/data directory', required=True)
    parser.add_argument('-o', '--output_dir', help='Output/results directory', required=True)
    parser.add_argument('-ng', '--num_groups', help='Number of canonical user groups', required=True)
    parser.add_argument('-ni', '--num_items', help='Number of items', required=True)
    parser.add_argument('-gdf', '--group_distributions_file', help='Normal of group params',
                        default='user_group_distributions.csv', required=False)
    parser.add_argument('-gpf', '--group_probabilities_file', help='Normalized size of groups',
                        default='user_group_probabilities.csv', required=False)
    parser.add_argument('-nu', '--num_users', help='Number of artificial users', default=450, required=False)
    parser.add_argument('-nt', '--num_trips', help='Num shopping trips per user', default=18, required=False)
    parser.add_argument('-ss', '--shelf_size', help='Number of items shown in each trip', default=6, required=False)
    parser.add_argument('-se', '--seed', help='Random seed for reproducibility', default=1234, required=False)

    args = parser.parse_args()
    random.seed(args.seed)
    np.random.seed(args.seed)
    print("Parsing arguments done.")

    print("Starting dataset builder.")
    db = dataset_builder.DatasetBuilder(args)
    db.generate_data_set()
    db.generate_reports()


if __name__ == '__main__':
    # Generate simulated dataset
    main()
