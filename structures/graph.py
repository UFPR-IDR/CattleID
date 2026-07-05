""" Graph structure to hold image description.

    Coded by Luiz.

    This file references the legacy/descriptor/luiz_graph.py file in the legacy code.
"""
from typing import List, Any

from utils import math_tools


class Graph:
    """ Represents a graph.

    Attributes:
    vertexes: List of vertexes of this graph
    """
    def __init__(self):
        self.vertexes: List[Vertex] = []
        self.avg_distances: float = 0.0
    
    def __str__(self):
        return("vertexes: %d  |  edges: %d" % (len(self.vertexes), self.count_edges()))

    def count_edges(self):
        """ Counts the edges of the graph. """
        n_edges = 0
        for v in self.vertexes:
            n_edges += len(v.neighbors)
        return n_edges//2

    def print_vertexes(self):
        """ Print all the graph's vertexes. """
        for v in self.vertexes:
            print(v)

    def remove_vertex(self, i: int): 
        """ Removes a vertex from the graph.
        
        Removes the i-th vertex by replacing it with the last vertex.

        Arguments:
        i: position of the vertex to be removed.
        """
        # Removes dead reference from each neighbor
        for neigh_of_vertex in self.vertexes[i].neighbors:
            # The list comprehension finds the index of neighbor to update
            self.vertexes[neigh_of_vertex.i].neighbors.pop([n.i for n in self.vertexes[neigh_of_vertex.i].neighbors].index(i))

        # Indexes range from 0..n-1. removing last element has simpler logic, since we don't need to move anything
        if i < len(self.vertexes)-1:
            self.vertexes[i].clear_info() # Clean all infos on the deleted vertex
            self.vertexes[i] = self.vertexes.pop()  # Replaces element by the last vertex
            self.vertexes[i].i = i  # Updates index for moved element
            
            # Updates indexes of neighbors for the moved vertex, otherwise they would still reference the final position
            for moved_neigh in self.vertexes[i].neighbors:
                # The list comprehension finds the index of neighbor to update
                self.vertexes[moved_neigh.i].neighbors[[n.i for n in self.vertexes[moved_neigh.i].neighbors].index(len(self.vertexes))].i = i  
        else:
            # If the element to remove is in the last index, just remove it
            self.vertexes.pop()
            
    def find_vertex(self, yx: List[int]):
        """ Returns a vertex based on (y,x) coordinates.
        
        Arguments:
        yx: List containing the coordinates of the vertex to be returned.

        Returns:
        vertex: Returns the found vertex. Returns -1 otherwise.
        """
        for vertex in self.vertexes :
            if (vertex.yx[0] == yx[0] and vertex.yx[1] == yx[1]) :
                return vertex

        print("ERROR: vertex not found")
        return -1

    def create_edge(self, i1: int, i2: int):
        """ Adds an edge to vertexes.
        
        Arguments:
        i1: The position of the first vertex.
        i2: The position of the second vertex.
        """
        self.vertexes[i1].add_neighbor(i2)
        self.vertexes[i2].add_neighbor(i1)

    def add_vertex(self, yx: List[int], list_neighs: List[int]):
        """ Adds a vertex to the graph.
        
        Arguments:
        yx: The position of the new vertex.
        list_neighs: The positions of all the neighbors of the vertex
        to be created.
        """
        new_pos = len(self.vertexes)  # Appends to the end of the list

        # TODO: verify if list_neighs should be included in this init
        self.vertexes.append(Vertex(self, new_pos, yx))
        
        for n in list_neighs:
            self.create_edge(new_pos, n)
            
        return self.vertexes[new_pos]
    
    def graph_fix_index(self):
        """ after altering the order of the vertexes in a graph using Top-K
        their internal index must update accordingly,
        or else we will mess up all sorts of things.
    
        arguments:
        graph: ordered graph, or messy graph
        """
    
        for v in self.vertexes:
            v.i = self.vertexes.index(v)
    
            for n in v.neighbors:
                n.i = self.vertexes.index(n.vertex)
    

## =====================================================================================================


class Vertex():
    """ Represents a vertex in the graph.

    Attributes:
    deviant: how much this vertex distincts from the median
    graph: The pointer to the graph where this vertex belongs.
    i: The index of this vertex in the graph.
    yx: List with (y,x) coordinates.
    neighbors: List with the neighbors of the vertex.
    """
    def __init__(self, graph: Graph, i: int, yx: List[int] = None, neighbors: List[Any] = None):
        self.graph: Graph = graph
        self.i = i  # This should be only used for printing, and should be equal to the element's index as of now
        self.yx = yx if yx is not None else []
        self.neighbors: List[Neighbor] = neighbors if neighbors is not None else [] # Ideally would be a set in order to disallow duplicates, 
                                                                                    # but we want ordering to prioritize neighbors later

    def __str__(self):
        print_i = -1 if self.i is None else self.i
        print_yx = [-1, -1] if self.yx is None else self.yx

        if (self.neighbors == None):
            return ("i: %d | yx: [%.0f, %.0f] | neighs: Empty" % (print_i, print_yx[0], print_yx[1]))
        
        print_neighs = ""
        for n in range(len(self.neighbors)):
            print_neighs += f"  | neigh {n}: {self.neighbors[n]}"
        
        return ("i: %d | yx: [%.0f, %.0f] | neighs: %s" % (print_i, print_yx[0], print_yx[1], print_neighs))
    
    def add_neighbor(self, neigh_i):
        """ Adds a neighbor to the vertex.
        
        Arguments:
        neigh_i: Index of the neighbor to be added.
        """

        # If neighbor already exists, update neighbor by removing it and adding it again
        if neigh_i in [getattr(n, 'i') for n in self.neighbors]:
            self.neighbors.pop([getattr(n,'i') for n in self.neighbors].index(neigh_i))

        self.neighbors.append(Neighbor(neigh_i, self.graph.vertexes[neigh_i], math_tools.euclidian_distance(self.graph.vertexes[self.i],self.graph.vertexes[neigh_i]), math_tools.calc_angle(self.graph.vertexes[self.i],self.graph.vertexes[neigh_i])))
        
    def switch_neighbor(self, a: int, b: int):
        """ Switch neighbors.
        
        Arguments:
        a: Index of the the first vertex.
        b: Index of the second vertex.
        """
        temp_neigh = self.neighbors[a]
        self.neighbors[a] = self.neighbors[b]
        self.neighbors[b] = temp_neigh
        
    def clear_info(self):
        """ Resets the values of a vertex. """
        self.i = 0
        self.graph = 0
        self.neighbors = []
        self.yx = []


class Neighbor():
    """ Represents a neighbor of a vertex.

    Attributes:
    i: The index of this neighbor in the graph.
    dist: The distance between the vertex and this neighbor.
    ang: The relative angle between the Vertex and this neighbor (horizontal, value in range [-180,180]).
    vertex: Pointer to the vertex this neighbor belongs.
    """
    def __init__(self, i: int, vertex: Vertex, dist: float, ang: float):
        self.i = i
        self.dist = dist
        self.ang = ang
        self.vertex = vertex 

    def __str__(self):
        return ("i: %d - dist: %.2f - ang: %.2f" % (self.i, self.dist, self.ang))
