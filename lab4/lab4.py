# NO ADDITIONAL IMPORTS!
from util import read_osm_data, great_circle_distance, to_local_kml_url

ALLOWED_HIGHWAY_TYPES = {
    'motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'unclassified',
    'residential', 'living_street', 'motorway_link', 'trunk_link',
    'primary_link', 'secondary_link', 'tertiary_link',
}

LINES="\n-----------------------\n"

DEFAULT_SPEED_LIMIT_MPH = {
    'motorway': 60,
    'trunk': 45,
    'primary': 35,
    'secondary': 30,
    'residential': 25,
    'tertiary': 25,
    'unclassified': 25,
    'living_street': 10,
    'motorway_link': 30,
    'trunk_link': 30,
    'primary_link': 30,
    'secondary_link': 30,
    'tertiary_link': 25,
}

def is_twoway(way):
    """
    Returns true is way is two way.
    """
    return way['tags'].get('oneway','no')!='yes'
	
def way_speed(way):
    """
    Returns way's speed, or best guess. 
    """
    return way['tags'].get('maxspeed_mph',DEFAULT_SPEED_LIMIT_MPH[way['tags']['highway']])

def build_auxiliary_structures(nodes_filename, ways_filename):
    """
    Create any auxiliary structures you are interested in, by reading the data
    from the given filenames (using read_osm_data)
    """
	#initialize max speed limit and the node adjacency dictionary
    max_speedlimit=float('-inf')
    adjacency={}
	
	#consider all ALLOWED ways in data
    for way in read_osm_data(ways_filename):
        if way['tags'].get('highway', None) in ALLOWED_HIGHWAY_TYPES:
            
			#speedlimit and maxspeedlimit
            speedlimit=way_speed(way)
            if max_speedlimit<speedlimit: max_speedlimit=speedlimit
			
			#initialize the loop to modify adjacency
            if way['nodes'][0] not in adjacency:
                adjacency[way['nodes'][0]]=set()
            twoway=is_twoway(way)	      

			#modify adjacency, considering speedlimit at each node through tuple
            for first,second in zip(way['nodes'],way['nodes'][1:]):
                adjacency.setdefault(first,set()).add((second,speedlimit))
                if second not in adjacency:
                    adjacency[second]=set()

                #if twoway, do the same for the opposite direction
                if twoway:
                    adjacency[second].add((first,speedlimit))
			   
	#considering only the relevant nodes, get their locations
    node_locs={}
    for node in read_osm_data(nodes_filename):
        if node['id'] in adjacency:
            node_locs[node['id']]=(node['lat'],node['lon'])
			
    return node_locs, adjacency, max_speedlimit

def trace_path(node):
    """
    Yields nodes connecting the best path.

    Args:
        node (integer): node ID

    Returns:
        list: nodes representing path
    """
    path=[]
    while node is not None:
        path.append(node[0])
        node=node[1]
    return path[::-1]

def generic_best_path(aux_structures, node1, node2, cost_func,heuristic_func):
    """
    Given two nodes, returns best path based on cost function and heuristic.

    Args:
        aux_structures (tuple): the result of calling build_auxiliary_structures 
        node1 (tuple): location of start node
        node2 (tuple): location of end node
        cost_func (function): distance, speed, or other
        heuristic_func (function): remaining distance, speed, or other
    Returns:
        list: best path
    """
    # initializations
    # NOTE: queue is a list of (heuristic, distance, (current_node, parent)) tuples!
    node_locs,adjacency,max_speedlimit=aux_structures
    queue=[(0,0,(node1,None))]
    visited=set()
    
    # BFS algorithm (using priority queue)
    while queue: # uses truthiness, i.e. loop stops when list is empty
        
		# BFS means FIFO, so need to pop earliest element. 
        _,cost,current=queue.pop(0) 
        node=current[0]
    
		#no need to reconsider already visited nodes
        if node in visited: 
            continue
        visited.add(node)
    
        # check if goal state was reached
        if node == node2:
            return trace_path(current)

        # properly add to priority queue
        if node in adjacency:
            for child in adjacency[node]:
                if child[0] not in visited:
                    new_cost=cost+cost_func(node,child)
                    priority=new_cost+heuristic_func(child[0])
                    queue.append((priority, new_cost,(child[0],current))); queue.sort()

	#if queue ends without finding node
    return None

def find_short_path_nodes(aux_structures, node1, node2):
    """
    Return the shortest path between the two nodes. Uses generic_best_path.

    Parameters:
        aux_structures: the result of calling build_auxiliary_structures
        node1: node representing the start location
        node2: node representing the end location

    Returns:
        a list of node IDs representing the shortest path (in terms of
        distance) from node1 to node2
    """
    node_locs=aux_structures[0]
    return generic_best_path(aux_structures,node1, node2,
                      lambda n1,n2: great_circle_distance(node_locs[n1],node_locs[n2[0]]),
                      lambda n: great_circle_distance(node_locs[node2],node_locs[n]))

def find_closest_node(node_locs,loc):
    """
    Returns node closesest to location.
    """
    closest=float('inf')
    for n,nloc in node_locs.items():
        dist=great_circle_distance(nloc,loc)
        if dist<closest:
            node=n
            closest=dist
    return node

def find_short_path(aux_structures, loc1, loc2):
    """
    Return the shortest path between the two locations

    Parameters:
        aux_structures: the result of calling build_auxiliary_structures
        loc1: tuple of 2 floats: (latitude, longitude), representing the start
              location
        loc2: tuple of 2 floats: (latitude, longitude), representing the end
              location

    Returns:
        a list of (latitude, longitude) tuples representing the shortest path
        (in terms of distance) from loc1 to loc2.
    """
    #get nodes corresponding to locs
    node_locs=aux_structures[0]
    node1=find_closest_node(node_locs,loc1)
    node2=find_closest_node(node_locs,loc2)

    #find path in terms of nodes
    path=find_short_path_nodes(aux_structures, node1, node2)

    #find and return corresponding path in terms of locs
    return [node_locs[n] for n in path] if path is not None else None

def find_fast_path(aux_structures, loc1, loc2):
    """
    Return the shortest path between the two locations, in terms of expected
    time (taking into account speed limits).

    Parameters:
        aux_structures: the result of calling build_auxiliary_structures
        loc1: tuple of 2 floats: (latitude, longitude), representing the start
              location
        loc2: tuple of 2 floats: (latitude, longitude), representing the end
              location

    Returns:
        a list of (latitude, longitude) tuples representing the shortest path
        (in terms of time) from loc1 to loc2.
    """
    #get nodes corresponding to locs
    node_locs, _ , max_speed_limit = aux_structures
    node1=find_closest_node(node_locs,loc1)
    node2=find_closest_node(node_locs,loc2)
    
    #find fastest path
    path=generic_best_path(aux_structures,node1, node2,
                      lambda n1,n2: great_circle_distance(node_locs[n1],node_locs[n2[0]])/n2[1],
                      lambda n: great_circle_distance(node_locs[node2],node_locs[n])/max_speed_limit)
    return [node_locs[n] for n in path] if path is not None else None






















if __name__ == '__main__':
    
    print(LINES)
    # How many nodes contained in Cambridge db? 6337751
    # NOTE: read_osm_data yields a generator object; loop is faster than len(list(x))
    j=0 
    for i in read_osm_data('resources/cambridge.nodes'): j+=1
    print(f'Nodes: {j}')
    
    #how many nodes have a 'name' among their tags? 19870
    j=0
    for i in read_osm_data('resources/cambridge.nodes'): 
        if 'name' in i['tags']:
            j+=1
    print(f'Nodes with a name: {j}')
    
    #ID of MIT address node? 1399811978
    for i in read_osm_data('resources/cambridge.nodes'): 
        if 'name' in i['tags']:
            if i['tags']['name']=='77 Massachusetts Ave':
                print('ID of MIT Address:',i['id']); break
    
    #how many ways in database? 838004
    j=0 
    for i in read_osm_data('resources/cambridge.ways'): j+=1
    print(f'Ways: {j}')

    #how many of them are one-way streets? 22677
    j=0 
    for i in read_osm_data('resources/cambridge.ways'):
        if 'oneway' in i['tags']:
            if i['tags']['oneway']=='yes':
                j+=1
    print(f'One-way ways: {j}')
    print(LINES)
	
	
	#distance between two specific locations (uses geodistance)
	print(great_circle_distance((42.36,-71.1),(42.36,-71.2)))
		
    
    #show output of axiliary structures
    print('AUXILIARY STRUCTURES')
    aux=build_auxiliary_structures('resources/mit.nodes','resources/mit.ways')
    print(LINES,aux[0],LINES,aux[1],LINES,aux[2],LINES)

    #output example with mit campus map
    n1=2; n2=7
    print(find_short_path_nodes(aux,n1,n2))
    
    