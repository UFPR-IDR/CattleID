"""
    This file references the legacy/matcher/no_ransac_bovine_matcher.py file in the legacy code.
"""
from typing import List, Any

from json.encoder import INFINITY

from structures import graph
from utils.math_tools import subtract_angles
from structures.matcher_groups import Local_group
from matchers.filter_local_groups import filter_spacial_size, filter_overlap
from descriptors.topK_lib import topK_order, topK_select_seeds

# testando
import random


SIMILARITY_STARTING_TRESHOLD = 15.0
SIMILARITY_TRESHOLD = 28.0
SIMILARITY_SPACIAL_THRESHOLD = 20.0
FILTER_STARTING_SIZE = 13.0
FILTER_FINAL_SIZE = 0.14
FILTER_SPACIAL_CORRECTNESS = 1

ANGLE_WEIGHT = 36.0
DISTANCE_WEIGHT = 1.2
CENTRAL_WEIGHT = 1.0


def match_already_in_local_groups(local_groups: List[Local_group], seed: List[List[int]]):
    """ Verifies for seed in local group.

    Returns True if seed is in a local group.

    Arguments:
    local_groups: Local group do search.
    seed: Seed to be searched inside this group.

    Returns:
    value: comparison result.
    """
    for lc in local_groups:
        for match in lc.group:
            if (seed == match):
                return True

    return False



#===========================================================================================



def vertex_similarity(vertex1: graph.Vertex, vertex2: graph.Vertex, filter: List[Any]) -> float:
    """ Computes the similarity between two vertexes

    Returns the similarity of each neighbor when comparing to the master neighbor.
    Closer to zero is best.

    Arguments:
    vertex1: The first vertex to compare.
    vertex2: The second vertex to compare.
    filter: Filters to be applied.

    Returns:
    similarity: The calculated similarity.
    """
    if (len(vertex1.neighbors) != len(vertex2.neighbors)):
        return INFINITY     # Comparison is nulled if number of neighbor is different

    sum = 0
    for neigh in range(len(vertex1.neighbors)):
        sum += filter[6] * abs(subtract_angles(vertex1.neighbors[neigh].ang, vertex2.neighbors[neigh].ang))
        sum += filter[7] * abs((vertex1.neighbors[neigh].dist) - (vertex2.neighbors[neigh].dist))
    
    similarity = filter[8] * (sum/(len(vertex1.neighbors)))
    return similarity


def recursive_part(group: List[List[List[int]]], vertex1: graph.Vertex, vertex2: graph.Vertex, filter: List[Any]):
    """ Accumulates neighbors in local group.

    Collects each similar neighbor and accumulates them in a local group.

    Arguments:
    group: List of neighbors
    vertex1: The first vertex to be analyzed.
    veretex2: The second vertex to be analyzed.
    filter: Filters to be applied while looking for groups.
    """
    for element in group:
        # If the match was already added, returns
        if not (vertex1.yx != element[0] and vertex2.yx != element[1]):
            return

    group.append([vertex1.yx , vertex2.yx])
    for i in range(len(vertex1.neighbors)):
        neigh1 = vertex1.neighbors[i].vertex
        neigh2 = vertex2.neighbors[i].vertex

        if (vertex_similarity(neigh1, neigh2, filter) < filter[4]):
            recursive_part(group, neigh1, neigh2, filter)


#===========================================================================================


def match_recursive(graph1: graph.Graph, graph2: graph.Graph, seed1: List[graph.Vertex] = None, seed2: List[graph.Vertex] = None, filters: List[Any] = None):
    """ Finds local groups

    Creates local groups by calculating the spatial similarity.

    Arguments:
    graph1: The firt graph to be searched.
    graph2: The second graph to be searched.
    filters: Filters to be applied while looking for groups.

    Returns:
    lists: Returns two lists, the first contains the individual matches and the group id
    of each match and the second list returns the match groups and its ids
    """

    local_groups: List[Local_group] = []
    local_group_correctness: List[int] = []

    #---

    if (seed1 == None):
        #seed1 = graph1.vertexes                    # All to All
        #seed1 = random.sample(graph1.vertexes, 15)  # Random elements
        topK_order(graph1)                          # Default Top-K Selection
        seed1 = topK_select_seeds(graph1, 15, 1)

    if (seed2 == None):
        #seed2 = graph2.vertexes                    # All to All
        #seed2 = random.sample(graph2.vertexes, 15)  # Random elements
        topK_order(graph2)                          # Default Top-K Selection
        seed2 = topK_select_seeds(graph2, 15, 1)

    #---

    if (filters == None):
        filter = [FILTER_STARTING_SIZE, FILTER_FINAL_SIZE, 
                  FILTER_SPACIAL_CORRECTNESS, SIMILARITY_STARTING_TRESHOLD,
                  SIMILARITY_TRESHOLD, SIMILARITY_SPACIAL_THRESHOLD, 
                  ANGLE_WEIGHT, DISTANCE_WEIGHT, CENTRAL_WEIGHT]
    else:
        filter = filters

    #------------------------------------------------------------------
    # Creates local groups with high similarity and ignores small groups
    for origin in seed1:

        for comp in seed2:    # TODO : mudar esse algoritmo guloso, para procurar o melhor grupo local em vez do primeiro
            # Vertex is not similar enough, continues
            if (vertex_similarity(origin, comp, filter) >= filter[3]) :
                continue
            
            # match is already in a local group, continues
            if (match_already_in_local_groups(local_groups, [origin.yx, comp.yx])) :
                continue

            # Calculates recursion
            local_group = []
            recursive_part(local_group, origin, comp, filter)

            # If the group is small, continues
            if (len(local_group) < filter[0]):
                continue
            
            # Saves the found groups
            local_groups.append(Local_group(local_group))
            local_group_correctness.append(0)
    
    #------------------------------------------------------------------
    # Calculates the spatial similarity between local groups
    for groupA in range(len(local_groups)):
        for groupB in range(len(local_groups)):
            if (groupA == groupB):
                continue
            
            if (local_groups[groupA].get_group_vector_diferentiality(local_groups[groupB]) <= filter[5]):
                local_group_correctness[groupA] += 1

    #------------------------------------------------------------------
    
    true_match_list: List[(int,int), (int,int)] = []
    true_match_list_group: List[int] = []

    #------------------------------------------------------------------

    # Applies filters
    size = max(len(graph1.vertexes), len(graph2.vertexes))
    filter_spacial_size(local_groups, local_group_correctness, filter, size)
    filter_overlap(local_groups)

    # Saves final groups
    for group_id in range(len(local_groups)):
        for match in local_groups[group_id].group:
            true_match_list.append(match)
            true_match_list_group.append(group_id)

    #------------------------------------------------------------------

    return true_match_list, true_match_list_group

