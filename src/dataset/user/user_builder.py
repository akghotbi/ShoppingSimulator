import numpy as np


class UserBuilder:
    """ Generates a user given its canonical group
        Capabilities:
            - Draws utilities,
            - Turns utilities into choice probabilities
            - Makes selection given choice probabilities and shelf assortment (trip items)
    """
    def __init__(self, group_distribution, user_id, user_group):
        self.group_mean, self.group_cov = group_distribution[0], group_distribution[1]
        self.user_id = user_id
        self.trip = 0
        self.user_group = user_group

        # Draw utilities
        self.user_utilities = self.draw_user_utilities()

        # Turn utilities to item probabilities
        self.user_item_probabilities = np.exp(self.user_utilities)
        self.user_item_probabilities = self.user_item_probabilities/np.sum(self.user_item_probabilities)

    def draw_user_utilities(self):
        """ Draws utilities from associated canonical Gaussian
            Returns:
                user_utilities: A vector of size = num_items.

            Note:
                Since, the model is logit only difference of utilities matter.
                Hence, we subtract the last utility from all vector entries.
        """
        user_utilities = np.random.multivariate_normal(mean=self.group_mean, cov=self.group_cov, size=1).ravel()
        user_utilities = user_utilities-user_utilities[user_utilities.size-1]
        return user_utilities

    def choose_from_items(self, trip_items):
        """ Simulates a simple multinomial process of size 1.

            Returns: A list containing
                user_id:    Happens to be the user index provided by constructor
                trip:       Current trip which ranges from 1 to num_trips
                choice:     Single choice made at this trip
        """
        p = self.user_item_probabilities[trip_items]/np.sum(self.user_item_probabilities[trip_items])
        choice = np.random.choice(a=trip_items, size=1, replace=False, p=p)
        self.trip = self.trip+1
        return [self.user_id, self.trip, choice]

    def get_utilities(self):
        return self.user_utilities
