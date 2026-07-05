"""
    This file references the legacy/utils/enrollment_protocol.py file in the legacy code.
"""
from typing import List, Dict


class EnrollmentGraph():
    """ Used in the enrollment algorithm.

    A graph is a adjacent list where each node is a segmented image
    and each edge has the similarity as the weight between two nodes.
    """
    def __init__(self):
        self.graph: Dict[str, List] = {}
        self.biggest_weight: float = 0
        self.smaller_weight: float = 999999

    def __len__(self):
        return len(self.graph.keys())

    def __str__(self):
        graph = str()   
        for source, destination in self.graph.items():
            graph += f"{source} --> {destination}\n"
        return graph[:-1] # Removes the last \n

    def get_biggest_weight(self):
        """ Returns the biggest weight """
        return self.biggest_weight

    def get_smaller_weight(self):
        """ Returns the smaller weight """
        return self.smaller_weight

    def get_neighs(self, node: str):
        """ Returns a list with (neigbour, cost) of a given node.
        
        Arguments:
        node: Path to the image node.

        Returns:
        nodes: The neighbors of the given node.
        """
        return self.graph[node]

    def get_avg_weight(self):
        """ Returns the average weight in the graph: sum(W)/2*len(graph) """
        total = 0
        avg = 0.0
        for frontier in self.graph.values():
            for _, cost in frontier:
                avg += cost
                total += 1
        
        try:
            avg = avg/total
        except ZeroDivisionError:
            avg = 0.0

        return avg

    def add_node(self, node: str):
        """ Adds a node e creates an empty adjency array.
        
        Arguments:
        node: Path to the image node.
        """
        if node not in self.graph:
            self.graph[node] = []

    def add_edge(self, node1: str, node2: str, cost: float):
        """ Adds an edge between two nodes with the given cost.
        
        Arguments:
        node1: Path to the image node.
        node2: Path to the image node.
        cost: Given cost between the nodes.
        """
        if node1 not in self.graph:
            self.graph[node1] = []
        if node2 not in self.graph:
            self.graph[node1] = []

        self.biggest_weight = max(self.biggest_weight, cost)
        self.smaller_weight = min(self.smaller_weight, cost)

        self.graph[node1].append((node2, cost))
        self.graph[node2].append((node1, cost))

    def prune_strategy(self, threshold: float):
        """ Removes every node on which the biggest edge is smaller then the threshold.
        
        Arguments:
        threshold: Value to consider when pruning.
        """
        prune = [] # Nodes to prune

        for node in self.graph:
            delta = 0
            for _, cost in self.graph[node]:
                delta = max(delta, cost)

            if delta < threshold:
                prune.append(node)

        # Removes the nodes to be pruned
        for node in prune:
            self.graph.pop(node)

    def listify(self) -> List[str]:
        """ Returns the list of images of the nodes is the graph """
        qualified = []
        for node in self.graph:
            qualified += [node]

        return qualified
