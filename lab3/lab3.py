# NO ADDITIONAL IMPORTS ALLOWED!
import pickle

#kevin bacon, the center of the initiali graph/tree, has actor ID 4724
BACON = 4724
#used for output formatting
def separate(): print('\n-------------------------\n')

#start lab
def transform_data(raw_data):
    """
    Returns new structure that maps each actor id to a
    set of people they have acted with (also IDs, not names).
    Additionally, for each movie it creates a set of 
    actor IDs that acted in that movie.
    """
    acted_with={}
    movie_actors={}
    for a1,a2,movie in raw_data:
        acted_with.setdefault(a1,set()).add(a2)
        acted_with.setdefault(a2,set()).add(a1)
        movie_actors.setdefault(movie,set()).update({a1,a2})
    return {'acted_with':acted_with,'movie_actors':movie_actors}
    
def acted_together(data, actor_id_1, actor_id_2):
    """
    Returns true if actors acted together.
    """
    return (actor_id_1==actor_id_2) or (actor_id_2 in data['acted_with'][actor_id_1])

def get_next_layer(acted_with,current_layer,parents_dictionary):
    """
    HELPER FUNCTION. Gets the next layer in the graph search
    """
    next_layer=set()
    for actor in current_layer:
        for neighbor in acted_with[actor]:
            if neighbor not in parents_dictionary:
                next_layer.add(neighbor)
                parents_dictionary[neighbor]=actor
    return next_layer

def actors_with_bacon_number(data, n):
    """
    Returns set of actors with Bacon number equal to 'n'.
    """
    #Initialize variables
    acted_with=data['acted_with']
    current_layer={BACON} #first layer, i.e. only Kevin Bacon
    parents_dictionary={BACON:None}
    
    for i in range(n):
        current_layer=get_next_layer(acted_with,current_layer,parents_dictionary)
        if not current_layer: #reduces execution time for unnecessarily large n
            return set()
    return current_layer

def bacon_path(data, actor_id):
    """
    Returns actor IDs representing path from BACON to the given actor ID.  Uses
    actor_to_actor_path.
    """
    return actor_to_actor_path(data, BACON, actor_id)
    
def get_path(parents_dictionary, node):
    """
    HELPER FUNCTION. Gets the path connecting specified node to original node
    """
    path=[]
    while node is not None:
        path.append(node)
        node=parents_dictionary[node]
    return path[::-1]
    
def actor_to_actor_path(data, actor_id_1, actor_id_2):
    """
    Returns path from actor_id_1 to actor_id_2. 
    Uses the actor_path function below. 
    """    
    return actor_path(data, actor_id_1, lambda node: node==actor_id_2)

def actor_path(data, actor_id_1, goal_test_function):
    """
    Returns path satisfying goal funcion. 
    Uses graph search algotrithm to obtain shortest path. 
    """    
    #Initialize variables
    acted_with=data['acted_with']
    current_layer={actor_id_1} #first layer
    parents_dictionary={actor_id_1:None}
    
    #search algorithm
    while current_layer:
        for node in current_layer:
            if goal_test_function(node):
                return get_path(parents_dictionary,node)
        current_layer=get_next_layer(acted_with,current_layer,parents_dictionary)
    return None

def actors_connecting_films(data, film1, film2):
    """
    Returns an actor path where the first actor acted in movie1, and the
    second actor acted in movie2. If no such path exists, returns None.
    """
    movie_to_actors = data['movie_actors']
    paths_found = []
    try:
        paths = [actor_path(data, a, lambda b: b in movie_to_actors[film2])
                        for a in movie_to_actors[film1]]
        return min((path for path in paths if path is not None), key=len)
    except ValueError as e:
        # If we take the min of an empty sequence (i.e  all paths are None)
        # we get a ValueError and thus there is no path.
        return None

def get_actor_name_map():
    """
    Helper function for get_movie_path.  Returns a mapping from actor names to
    ID numbers.
    """
    with open('resources/names.pickle', 'rb') as f:
        return pickle.load(f)

def get_movie_name_map():
    """
    Helper function for get_movie_path.  Returns a mapping from movie names to
    ID numbers.
    """
    with open('resources/movies.pickle', 'rb') as f:
        return pickle.load(f)

def get_actors_to_movie_db(data):
    """
    Helper function for get_movie_path.  Returns a mapping from pairs of actors
    to the ID number of a movie in which they acted together.
    """
    out = {}
    for a1, a2, m in data:
        out[frozenset({a1, a2})] = m
    return out

def get_movie_to_actors_db(data):
    """
    Returns a mapping from movies to the set of actors who acted in the movie.
    """
    out = {}
    for a1, a2, m in data:
        out.setdefault(m, set()).update({a1, a2})
    return out

def get_movie_path(data, actor_name_1, actor_name_2):
    """
    Returns a list of movie names that connect the two given actors (here given
    as names, not as IDs)
    """
    # Create mappings
    movie_db = get_actors_to_movie_db(data)
    movie_name_db = {v: k for k,v in get_movie_name_map().items()}
    id_from_name = get_actor_name_map()
    
    # Next, determine the ID numbers of the given actors.
    actor_id_1 = id_from_name[actor_name_1]
    actor_id_2 = id_from_name[actor_name_2]

    # Find the path between them in terms of actors normally.
    actor_path = actor_to_actor_path(data, actor_id_1, actor_id_2)

    # Look up the movie ID numbers that connect each successive pair of actors.
    movie_id_path = [movie_db[frozenset(x)] for x in zip(actor_path, actor_path[1:])]

    # And, finally, convert the movie ID numbers into names.
    return [movie_name_db[i] for i in movie_id_path]


if __name__ == '__main__':

    with open('resources/small.pickle', 'rb') as f:
        smalldb = pickle.load(f)
    
    
    with open('resources/names.pickle', 'rb') as f:
        namesdb = pickle.load(f)

    #look up Patricia Hodge's ID
    print(namesdb['Patricia Hodge']) #175977
    separate()

    #look up name corresponding to 1272929
    idsdb={v:k for k,v in namesdb.items()}
    print(idsdb[1272929]) #Jaden Martin
    separate()

	#set of actors with Bacon number of 6
    with open('resources/large.pickle', 'rb') as f:
        largedb = pickle.load(f)
    print(actors_with_bacon_number(transform_data(largedb),6)) # {1367972, 1345461, 1345462, 1338716}
    separate()

    #test bacon path
    print(bacon_path(transform_data(largedb),1272929)) #[4724, 2295, 2598, 1272929]
    separate()

    #test actor to actor path
    print(actor_to_actor_path(transform_data(largedb),1367972,1272929)) #[1367972, 1338712, 105288, 98132, 12797, 1272929]
    separate()
    
    #movie path
    print(get_movie_path(transform_data(smalldb), 'Kevin Bacon','Julia Roberts'))
    separate()