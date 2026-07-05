"""
    This file has been created after initial refactoring
"""

from ioHandler.path_handler import *
from os import remove
from matchers.matcher import match_recursive
from descriptors.graph_generator import graph_routine


def protocol_min_session_images(file_paths: list, min_qtd: int = 2, delete: bool = False) :
    """ 
    Filter sessions that have less than a set amount of images,
    returns a list of all images inside valid sessions.\n
    [CAUTION] If delete is set, this function also removes files filtered.

    :param file_paths: list of files
    :param min_qtd: value to filter sessions (default=2)
    :param delete: check to delete filtered files (default=false)

    :return: List of files from valid sessions
    """
    filtered_images = []
    all_animals = pathfinder_get_all_animals(file_paths)

    for animal in all_animals :
        animal_files = pathfinder_filter_animal(file_paths, animal)
        all_sessions = pathfinder_get_all_sessions(animal_files)

        for session in all_sessions :
            session_files = pathfinder_filter_session(animal_files, session)

            # Apenas mantemos imagens que estao em sessoes validas
            if (len(session_files) > min_qtd) :
                for file in session_files :
                    filtered_images.append(file)
            else :
                if (delete) :
                    for file in session_files :
                        remove(file)

    return filtered_images


def protocol_min_sessions(file_paths: list, min_qtd: int = 1, delete: bool = False) :
    """ 
    Filter animais that have less than a set amount of sessions,
    returns a list of all images from valid animals.\n
    [CAUTION] If delete is set, this function also removes files filtered.

    :param file_paths: list of files
    :param min_qtd: value to filter animals (default=1)
    :param delete: check to delete filtered files (default=false)

    :return: List of files from valid sessions
    """
    filtered_images = []
    all_animals = pathfinder_get_all_animals(file_paths)

    for animal in all_animals :
        animal_files = pathfinder_filter_animal(file_paths, animal)
        all_sessions = pathfinder_get_all_sessions(animal_files)

        # Apenas mantemos sessoes de animais validos
        if (len(all_sessions) > min_qtd) :
            for file in animal_files :
                filtered_images.append(file)
        else :
            if (delete) :
                for file in animal_files :
                    remove(file)

    return filtered_images


#--


def protocol_similarity(file: str, file_paths: list, min_qtd: int = 2, sim_threshold: float = 0.17, delete: bool = False) :
    """ 
    Test a file for good similarity within the same session,
    returns whether or not it passed.\n
    [CAUTION] If delete is set, this function will also remove the file if failed.

    :param file: the file to test
    :param intra_files: list of all files
    :param min_qtd: necessary amount of good matches (default=2)
    :param sim_threshold: similarity needed to be considered a good match (default=0.17)
    :param delete: check to delete filtered files (default=false)

    :return: Boolean If the file passed the protocol or failed
    """
    qtd_good_matches = 0
    graph = graph_routine(file)

    intra_files = pathfinder_filter_both(file_paths, pathfinder_get_session(file), pathfinder_get_animal(file))

    for intra_file in intra_files :
        if (intra_file == file) :
            continue

        graph_intra = graph_routine(intra_file)
        matchs, match_groups = match_recursive(graph, graph_intra)

        sim_obtida = (2 * len(matchs))/(len(graph_intra.vertexes)+len(graph.vertexes))
        if (sim_obtida >= sim_threshold) :
            qtd_good_matches += 1

    if (qtd_good_matches >= min_qtd) :
        return True
    else :
        if (delete) :
            remove(file)

    return False


def protocol_similarity_full(file_paths: list, min_qtd: int = 2, sim_threshold: float = 0.17, delete: bool = False) :
    """ 
    Filter images that fail the similarity protocol,
    returns a list of all valid images.\n
    [CAUTION] If delete is set, this function also removes files filtered.

    :param file_paths: list of files
    :param min_qtd: necessary amount of matches (default=2)
    :param sim_threshold: similarity needed to be considered a good match (default=0.17)
    :param delete: check to delete filtered files (default=false)

    :return: List of valid images
    """
    filtered_images = []
    
    for file in file_paths :
        if (protocol_similarity(file, file_paths, min_qtd, sim_threshold, delete)) :
            filtered_images.append(file)

    return filtered_images