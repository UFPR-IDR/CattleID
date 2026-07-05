"""
    This file has been created after initial refactoring
"""
from math import sqrt


class Local_group:
    """ Defines local group. """
    def __init__(self, group = None):
        self.group = []
        self.diferential_vector = [0, 0]
        
        if (group != None) :
            self.group = group
            self.calculate_diferentiality()


    def __str__(self):
        return("Group: " + self.group + "  |  diferential_vector: " + self.diferential_vector)


    def calculate_diferentiality(self):
        """ Calculates the differential vector from B to A. """
        self.diferential_vector = [0, 0]
        
        centerA = [0, 0]
        centerB = [0, 0]

        for match in self.group :
            centerA[0] += match[0][0]
            centerA[1] += match[0][1]
            centerB[0] += match[1][0]
            centerB[1] += match[1][1]

        centerA[0] /= len(self.group)
        centerA[1] /= len(self.group)
        centerB[0] /= len(self.group)
        centerB[1] /= len(self.group)
        
        self.diferential_vector = [centerB[0] - centerA[0] , centerB[1] - centerA[1]]


    def get_group_vector_diferentiality(self, other_local_group: "Local_group"):
        """ Calculates the vector difference of the spatial variation of 2 different local groups.
        
        Arguments:
        other_local_group: The local group to be compared to the current object.

        Returns:
        diff: The difference between both local groups.
        """
        vector = [
            self.diferential_vector[0] - other_local_group.diferential_vector[0],
            self.diferential_vector[1] - other_local_group.diferential_vector[1]
        ]
        
        sum = vector[0]**2 + vector[1]**2
        diff = sqrt(sum)
        return diff


    def group_size_comp(self, other_local_group: "Local_group"):
        """ Compares the sizes of 2 local groups

        Returns True if this_group > other_group, False otherwise .

        Arguments:
        other_local_group: The local group to be compared to the current object.

        Returns:
        value: comparison result
        """
        return (len(self.group) > len(other_local_group.group))
