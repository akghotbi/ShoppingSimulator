import numpy as np


class DoEBuilder:
    """ Generates assortments of products on shelf for each shopper trip.
    """
    def __init__(self, num_items, num_trips, shelf_size):
        self.num_running_trips = 0
        # Item counts across user shopping trips
        self.item_trip_counts = np.zeros(num_items)
        self.doe = np.zeros([num_trips, num_items])
        self.num_items = num_items
        self.num_trips = num_trips
        self.shelf_size = shelf_size

        # Average chance of each product to appear on shelf
        self.item_balanced_view_prob = shelf_size/num_items

        # Start with flat item draw probabilities
        self.item_draw_probs = np.ones(self.num_items)/self.num_items

    def reset(self):
        """ Resets the DoE generator before user starts
        """

        # Draw probabilities back to flat
        self.item_draw_probs = np.ones(self.num_items)/self.num_items

        # Reset number of shopping trips and item counts across trips
        self.num_running_trips = 0
        self.item_trip_counts = np.zeros(self.num_items)



    def update_probabilities(self):
        """ A simple method to update item draw probabilities after each shelf
            to avoid favoring an item by chance. It reduces the sampling variance
            by learning from what has been drawn for user to this point and compare
            it with the ideal/theoretical count limit for an item.
            If close to theoretical count limit the probability of choosing the
            item goes down to avoid over-sampling.
        """
        ideal_counts = self.item_balanced_view_prob*(1+self.num_running_trips)
        current_portions = self.item_trip_counts / ideal_counts
        # To avoid edge cases 0.999 is used instead of 1.0
        current_portions[current_portions >= 1.0] = 0.999
        self.item_draw_probs = 1.0 - current_portions
        if np.all(self.item_draw_probs == 0.0):
            self.item_draw_probs = np.ones(self.num_items) / self.num_items
        else:
            self.item_draw_probs = self.item_draw_probs/np.sum(self.item_draw_probs)

    def next_shelf(self):
        """ Generates next shelf assortment for user.
            Updates draw probabilities at the end for next shelf.

            Returns:
                idx:    Index of items available on shelf (size = shelf_size)
                x:      Dummy coded representation of idx (size = num_items)
        """
        if self.num_running_trips >= self.num_trips:
            raise ValueError('The number of shipping trips exceeds what is expected: {0:d}'.format(self.num_trips))

        idx = np.random.choice(a=self.num_items, size=self.shelf_size, replace=False, p=self.item_draw_probs)
        x = np.zeros(self.num_items)
        x[idx] = 1
        self.doe[self.num_running_trips, idx] = 1
        self.item_trip_counts += x
        self.num_running_trips += 1
        self.update_probabilities()

        return idx, x
