"""
    This file references the legacy/matcher/similarity_calcs.py file in the legacy code.
"""
from structures.graph import Graph


def similarity_NOR(matches:list, graph1: Graph, graph2: Graph):
    """ Calculates similarity without using RANSAC

    Parameters:
    matches: List of matches
    graph1: First graph
    graph2: Second graph
    
    Returns:
    similarity: The calculated similarity between the graphs
    """
    try:
        g1, g2 = len(graph1.vertexes), len(graph2.vertexes)
        similarity = (2*len(matches))/(g1 + g2)
    except ZeroDivisionError:
        similarity = 0

    return similarity


def similarity_WR(inliers:list, graph1: Graph, graph2: Graph):
    """ Calculates similarity using RANSAC

    Parameters:
    inliers: List of inliers
    graph1: First graph
    graph2: Second graph
    
    Returns:
    similarity: The calculated similarity between the graphs
    """
    try:
        g1, g2 = len(graph1.vertexes), len(graph2.vertexes)
        similarity = (2*sum(inliers))/(g1 + g2)
    except ZeroDivisionError:
        similarity = 0

    return similarity


def similarity_graph(inliers: list, num_vertexes: int):
    """Calculo de similaridade usando resultado do Ransac"""

    """ Calculates similarity using RANSAC's results

    Parameters:
    inliers: List of inliers
    num_vertexes: Total number of vertexes

    Returns:
    similarity: The calculated similarity
    """
    try:
        similarity = sum(inliers)/num_vertexes
    except ZeroDivisionError:
        similarity = 0
        
    return similarity


def similarity_no_ransac(matches, num_vertexes):
    """ Calculates similarity without RANSAC, only using matches

    Parameters:
    matches: List of matches
    num_vertexes: Total number of vertexes

    Returns:
    similarity: The calculated similarity
    """
    try:
        similarity = len(matches)/num_vertexes
    except ZeroDivisionError:
        similarity = 0
    
    return similarity
