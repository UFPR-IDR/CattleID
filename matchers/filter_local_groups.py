"""
    This file has been created after initial refactoring
"""
from typing import List, Any
import math

from structures.matcher_groups import *




def check_vertex_overlap(group_id: int, all_local_groups: List[Local_group]) :
    """ Check if groups have a vertex overlap

    Returns True if group_id has overlap and is smaller than the group
    that caused a repetition.

    Arguments:
    group_id: The localization of the group in the groups list.
    all_local_groups: Reference group list.

    Returns:
    value: comparison result
    """
    for origin_match in all_local_groups[group_id].group:
        for other_group in range(len(all_local_groups)) :
            # Don't compare the group with itself
            if (other_group == group_id) :
                continue
            
            # Skip if this is the smaller group between the two
            if (all_local_groups[group_id].group_size_comp(all_local_groups[other_group])) :
                continue

            # Compares matches between origin and other
            for comp_match in all_local_groups[other_group].group:
                if (origin_match[0] == comp_match[0]):
                    return True
                else :
                    if (origin_match[1] == comp_match[1]) :
                        return True

    return False


def filter_spacial_size(local_groups: List[Local_group], local_group_correctness: List[int], filter: List[Any], size: int):
    """ Filter local groups spatially and in size

    Removes every local group that has no spatial relationship and is small in size.

    Arguments:
    local_groups: List containing the found groups.
    local_group_correctness: TODO
    filter: Filters to be applied on groups.
    size: Size to use for prunning.

    Returns:
    local_groups: The filtered local groups.
    """
    group_id = len(local_groups) - 1
    while (group_id >= 0):
        if (local_group_correctness[group_id] <= filter[2] and len(local_groups[group_id].group) < (size * filter[1]) ):
            local_groups.pop(group_id)
        else :
            if (math.hypot(local_groups[group_id].diferential_vector[0], local_groups[group_id].diferential_vector[0]) > 100):
                local_groups.pop(group_id)

        group_id -= 1

    return local_groups


def filter_overlap(local_groups: List[Local_group]):
    """ Filter local groups by overlap

    When local groups have an overlap, removes the smaller one.

    Arguments:
    local_groups: The list local groups found.

    Returns:
    local_groups: A new list removing any group overlap.
    """
    group_id = len(local_groups) - 1
    while (group_id >= 0):
        if (check_vertex_overlap(group_id, local_groups)):
            local_groups.pop(group_id)

        group_id -= 1

    return local_groups
