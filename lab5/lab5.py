"""6.009 Lab -- Six Double-Oh Mines"""
# NO IMPORTS ALLOWED!

def dump(game):
    """
    Prints a human-readable version of a game (provided as a dictionary)
    """
    for key, val in sorted(game.items()):
        if isinstance(val, list) and val and isinstance(val[0], list):
            print(f'{key}:')
            for inner in val:
                print(f'    {inner}')
        else:
            print(f'{key}:', val)

# 2-D IMPLEMENTATION

def new_game_2d(num_rows, num_cols, bombs):
    """
    Start a new game. Uses new_game_nd.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'mask' fields adequately initialized.

    Parameters:
       num_rows (int): Number of rows
       num_cols (int): Number of columns
       bombs (list): List of bombs, given in (row, column) pairs, which are
                     tuples

    Returns:
       A game state dictionary

    >>> dump(new_game_2d(2, 4, [(0, 0), (1, 0), (1, 1)]))
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    mask:
        [False, False, False, False]
        [False, False, False, False]
    state: ongoing
    """
    return new_game_nd((num_rows,num_cols),bombs)

def dig_2d(game, row, col):
    """
    Reveal the cell at (row, col), and, in some cases, recursively reveal its
    neighboring squares. Uses dig_nd.

    Update game['mask'] to reveal (row, col).  Then, if (row, col) has no
    adjacent bombs (including diagonally), then recursively reveal (dig up) its
    eight neighbors.  Return an integer indicating how many new squares were
    revealed in total, including neighbors, and neighbors of neighbors, and so
    on.

    The state of the game should be changed to 'defeat' when at least one bomb
    is visible on the board after digging (i.e. game['mask'][bomb_location] ==
    True), 'victory' when all safe squares (squares that do not contain a bomb)
    and no bombs are visible, and 'ongoing' otherwise.

    Parameters:
       game (dict): Game state
       row (int): Where to start digging (row)
       col (int): Where to start digging (col)

    Returns:
       int: the number of new squares revealed

    >>> game = {'dimensions': (2, 4),
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'mask': [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 3)
    4
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    mask:
        [False, True, True, True]
        [False, False, True, True]
    state: victory

    >>> game = {'dimensions': [2, 4],
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'mask': [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 0)
    1
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: [2, 4]
    mask:
        [True, True, False, False]
        [False, False, False, False]
    state: defeat
    """
    return dig_nd(game,(row,col))

def render_2d(game, xray=False):
    """
    Prepare a game for display.

    Returns a two-dimensional array (list of lists) of '_' (hidden squares), '.'
    (bombs), ' ' (empty squares), or '1', '2', etc. (squares neighboring bombs).
    game['mask'] indicates which squares should be visible.  If xray is True (the
    default is False), game['mask'] is ignored and all cells are shown.

    Parameters:
       game (dict): Game state
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['mask']

    Returns:
       A 2D array (list of lists)

    >>> render_2d({'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'mask':  [[False, True, True, False],
    ...                   [False, False, True, False]]}, False)
    [['_', '3', '1', '_'], ['_', '_', '1', '_']]

    >>> render_2d({'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'mask':  [[False, True, False, True],
    ...                   [False, False, False, True]]}, True)
    [['.', '3', '1', ' '], ['.', '.', '1', ' ']]
    """
    return render_nd(game, xray)

def render_ascii(game, xray=False):
    """
    Render a game as ASCII art.

    Returns a string-based representation of argument 'game'.  Each tile of the
    game board should be rendered as in the function 'render_2d(game)'.

    Parameters:
       game (dict): Game state
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['mask']

    Returns:
       A string-based representation of game

    >>> print(render_ascii({'dimensions': (2, 4),
    ...                     'state': 'ongoing',
    ...                     'board': [['.', 3, 1, 0],
    ...                               ['.', '.', 1, 0]],
    ...                     'mask':  [[True, True, True, False],
    ...                               [False, False, True, False]]}))
    .31_
    __1_
    >>> print(render_ascii({'dimensions': (4, 8),
    ...                     'state': 'ongoing',
    ...                     'board': [[0,0,0,0,0,0,0,0],
    ...                               [0,0,0,0,0,1,1,1],
    ...                               [0,0,0,0,1,2,0,2], 
    ...                               [1,2,1,2,2,1,2,1]],
    ...                     'mask':  [[True,True,True,True,True,True,True,True,],
    ...                               [True,True,True,True,True,True,True,True,],
    ...                               [True,True,True,True,True,True,False,False], 
    ...                               [True,True,True,True,True,False,False,False]]}))
    <BLANKLINE>        
         111
        12__
    12122___

    """
    return '\n'.join([''.join(row) for row in render_2d(game, xray)])
    
# N-D IMPLEMENTATION

def make_board_nd(dimensions,value):
    """
    Builds n-dimensional board filled with specified value. 
    
    >>> make_board_nd((2,2),0)
    [[0, 0], [0, 0]]
    >>> make_board_nd((1,2,1),False)
    [[[False], [False]]]
    """
    # recursion base case
    if len(dimensions)==1:
        return [value]*dimensions[0]
    return [make_board_nd(dimensions[1:],value) for dim in range(dimensions[0])]

def get_value_nd(board,loc):
    """
    Gets value at specified location on the board. 

    Args:
        board (list): list of lists representing board
        loc (tuple): tuple describing location on board

    Returns:
        Value at that location

    >>> board=make_board_nd((2,2),0)
    >>> get_value_nd(board,(0,0))
    0
    """
    # recursion base case
    if len(loc)==1:
        return board[loc[0]]
    return get_value_nd(board[loc[0]],loc[1:])

def set_value_nd(board, loc, val):
    """
    Sets value at specified location on the board. 

    Args:
        board (list): list of lists representing board
        loc (tuple): tuple describing location on board
    
    >>> board=make_board_nd((2,2),0)
    >>> set_value_nd(board,(0,0),1)
    
    >>> board
    [[1, 0], [0, 0]]
    """
    # recursion base case
    if len(loc)==1:
        board[loc[0]] = val
    else:
        set_value_nd(board[loc[0]],loc[1:],val)
    
def neighbors_nd(loc,dims):
    """
    Yields dims-long tuples where each tuple is a (valid) neighbor of loc.
    NOTE: Includes loc itself.
    """
    # recursion base case: no further coordinate to add
    if len(dims)==0:
        yield tuple() 
    else:
        # recusion principle: decrease problem size by running 
        # same function on smaller subsection
        for i in neighbors_nd(loc[1:],dims[1:]):
            # given first dimension, consider (-1,0,+1)  
            for j in (loc[0]-1,loc[0],loc[0]+1):
                # valid if in range
                if 0 <= j < dims[0]:
                    yield (j,)+i  

def coords_generator_nd(dims):
    """
    Yields over index of n-dim board. 
    Generator's recursive structure is very similar to neighbors_nd.
    """
    if len(dims)==0:
        yield tuple()
    else:
        # uses yield from to express it more succintly, 
        # but same logic as neighbors_nd.
        yield from ((j,)+i for i in coords_generator_nd(dims[1:]) for j in range(dims[0]))        

def new_game_nd(dimensions, bombs):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'mask' fields adequately initialized.


    Args:
       dimensions (tuple): Dimensions of the board
       bombs (list): Bomb locations as a list of lists, each an
                     N-dimensional coordinate

    Returns:
       A game state dictionary

    >>> g = new_game_nd((2, 4, 2), [(0, 0, 1), (1, 0, 0), (1, 1, 1)])
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    mask:
        [[False, False], [False, False], [False, False], [False, False]]
        [[False, False], [False, False], [False, False], [False, False]]
    state: ongoing
    """
    # build mask and empty board 
    mask = make_board_nd(dimensions,False)
    board = make_board_nd(dimensions,0) 
    
    # place bombs on board, and set number of bombs in its surrounding cells 
    for loc in bombs: 
        set_value_nd(board,loc,'.')
        for neighbor in neighbors_nd(loc,dimensions):
            val=get_value_nd(board, neighbor)
            if isinstance(val, int):    
                set_value_nd(board,neighbor,val+1)

    return {'dimensions': dimensions,
            'board' : board,
            'mask' :mask,
            'state': 'ongoing'} 

def is_victory(game):
    """ 
    Returns True if all locations on board without 
    bombs are now visible, else False.
    """
    for loc in coords_generator_nd(game['dimensions']):
        # if not a mine, nor visible 
        if isinstance(get_value_nd(game['board'],loc),int):
            if not get_value_nd(game['mask'],loc):
                return False
    return True

def dig_nd(game, coordinates):
    """
    Recursively dig up square at coords and neighboring squares.

    Update the mask to reveal square at coords; then recursively reveal its
    neighbors, as long as coords does not contain and is not adjacent to a
    bomb.  Return a number indicating how many squares were revealed.  No
    action should be taken and 0 returned if the incoming state of the game
    is not 'ongoing'.

    The updated state is 'defeat' when at least one bomb is visible on the
    board after digging, 'victory' when all safe squares (squares that do
    not contain a bomb) and no bombs are visible, and 'ongoing' otherwise.

    Args: 
       coordinates (tuple): Where to start digging

    Returns: 
       int: number of squares revealed

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'mask': [[[False, False], [False, True], [False, False], [False, False]],
    ...               [[False, False], [False, False], [False, False], [False, False]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 3, 0))
    8
    >>> dump(g)
    board: 
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    mask: 
        [[False, False], [False, True], [True, True], [True, True]]
        [[False, False], [False, False], [True, True], [True, True]]
    state: ongoing
    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'mask': [[[False, False], [False, True], [False, False], [False, False]],
    ...               [[False, False], [False, False], [False, False], [False, False]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 0, 1))
    1
    >>> dump(g)
    board: 
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    mask:
        [[False, True], [False, True], [False, False], [False, False]]
        [[False, False], [False, False], [False, False], [False, False]]
    state: defeat
    """
    # if already visible or game not ongoing return zero, else set as visible 
    # [this is the base case recursion, needed to count revealed cells]
    if game['state']!='ongoing' or get_value_nd(game['mask'],coordinates):
        return 0
    set_value_nd(game['mask'],coordinates,True)
    
    #extract corresponding value
    this_value=get_value_nd(game['board'],coordinates)

    # if defeat change game state
    if this_value =='.':
        game['state']='defeat'
        return 1

    # set 'revealed' count to 1, and recursively reveal empty neighbors
    revealed=1
    if this_value==0: # i.e. if not bomb nor adjacent to bomb
        for n in neighbors_nd(coordinates,game['dimensions']):
            # recursively check neighbors AND increase 'revealed' count
            revealed+=dig_nd(game, n)

    # check if victory
    if is_victory(game):
        game['state']='victory'
    
    return revealed

def render_nd(game, xray=False):
    """
    Prepare the game for display.

    Returns an N-dimensional array (nested lists) of '_' (hidden squares),
    '.' (bombs), ' ' (empty squares), or '1', '2', etc. (squares
    neighboring bombs).  The mask indicates which squares should be
    visible.  If xray is True (the default is False), the mask is ignored
    and all cells are shown.

    Args:
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    the mask

    Returns:
       An n-dimensional array of strings (nested lists)

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'mask': [[[False, False], [False, True], [True, True], [True, True]],
    ...               [[False, False], [False, False], [True, True], [True, True]]],
    ...      'state': 'ongoing'}
    >>> render_nd(g, False)
    [[['_', '_'], ['_', '3'], ['1', '1'], [' ', ' ']],
     [['_', '_'], ['_', '_'], ['1', '1'], [' ', ' ']]]

    >>> render_nd(g, True)
    [[['3', '.'], ['3', '3'], ['1', '1'], [' ', ' ']],
     [['.', '3'], ['3', '.'], ['1', '1'], [' ', ' ']]]
    """
    out=make_board_nd(game['dimensions'],None)
    for loc in coords_generator_nd(game['dimensions']):
        visible = get_value_nd(game['mask'],loc)
        val = get_value_nd(game['board'],loc)
        set_value_nd(out,loc,'_' if not visible and not xray else ' ' if val==0 else str(val))
    return out

if __name__ == "__main__":
    # Test with doctests. Helpful to debug individual lab.py functions.
    import doctest
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    #doctest.testmod(optionflags=_doctest_flags) #runs ALL doctests

    # Alternatively, can run the doctests JUST for specified function/methods,
    # e.g., for render_2d or any other function you might want.  To do so, comment
    # out the above line, and uncomment the below line of code. This may be
    # useful as you write/debug individual doctests or functions.  Also, the
    # verbose flag can be set to True to see all test results, including those
    # that pass.
    
    doctest.run_docstring_examples(render_nd, globals(), optionflags=_doctest_flags, verbose=False)









