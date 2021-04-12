"""6.009 Lab 6 -- Boolean satisfiability solving"""

import sys
sys.setrecursionlimit(10000)
# NO ADDITIONAL IMPORTS

#PART 1

def satisfying_assignment(formula):
    """
    Find a satisfying assignment for a given CNF formula.
    Returns that assignment if one exists, or None otherwise.

    >>> satisfying_assignment([])
    {}
    >>> x = satisfying_assignment([[('a', True), ('b', False), ('c', True)]])
    >>> x.get('a', None) is True or x.get('b', None) is False or x.get('c', None) is True
    True
    >>> satisfying_assignment([[('a', True)], [('a', False)]])
    """
    return solver(convert_formula(formula))

def convert_formula(formula):
    """
    Returns same formula, but with clauses expressed as sets
    of tuples rather than lists of tuples. Formula remains
    a list. 
    """
    return [set(clause) for clause in formula]

def get_from_set(set_):
    """
    Extracts element from a set without modifying set itself,
    as set.pop() otherwise would.
    """
    for e in set_: return e

def expand(formula,var,val):
    """
    Returns updated, simplified formula after assigning the 
    variable var to value val.

    In practice, this will have two effects:
    1) REMOVE clauses that contain (var, val) literals,
       because already satisfied, i.e. they are true.
    2) MODIFY clauses that contain (var, not val) literals; these must
       be satisfied by one of the other literals, hence we can delete 
       this literal. 
    """
    return [clause - {(var, not val)} # group 2 modified here
            for clause in formula 
            if (var,val) not in clause] # group 1 removed here

def solver(formula):
    """
    Find a satisfying assignment for a given CNF formula.
    Returns that assignment if one exists, or None otherwise.

    >>> satisfying_assignment([])
    {}
    >>> x = satisfying_assignment([[('a', True), ('b', False), ('c', True)]])
    >>> x.get('a', None) is True or x.get('b', None) is False or x.get('c', None) is True
    True
    >>> satisfying_assignment([[('a', True)], [('a', False)]])
    """
    # dictionary initializing output solution
    assignments={}

    # check and simplify unit clauses
    for clause in formula:
        # if clause is a unit clause
        if len(clause)==1:
            # extract random literal from clause
            var,val=get_from_set(clause)
            # make assignment such that unit clause is true
            assignments[var] = val
            # update rest of the formula with such assignment
            formula = expand(formula,var,val)

    # RECURSION BASE CASE 1: found one of possible solutions
    # NOTE: since I eliminate clauses once satisfied, list is 
    # empty when all clauses are satisfied. 
    if not formula:
        return assignments

    # RECURSION BASE CASE 2: impossible due to contradiction
    # NOTE: if any of the clauses is false, then no solution
    if not all(formula):
        return None

    # CORE OF RECURSION: recursive simplification of CNF formula
    var, val = get_from_set(formula[0])
    for attempt in (val, not val): # e.g try True, if no success try False    
        assignments[var] = attempt
        new_assignments = solver(expand(formula,var,attempt))
        if new_assignments is not None:
            assignments.update(new_assignments)
            return assignments

    # if we get to this line, neither attempt yields a solution
    return None

#PART 2

def boolify_scheduling_problem(student_preferences, session_capacities):
    """
    Convert a quiz-room-scheduling problem into a Boolean formula.

    student_preferences: a dictionary mapping a student name (string) to a set
                         of session names (strings) that work for that student
    session_capacities: a dictionary mapping each session name to a positive
                        integer for how many students can fit in that session

    Returns: a CNF formula encoding the scheduling problem, as per the
             lab write-up
    We assume no student or session names contain underscores.
    """
    # gather all rules (i.e. functions) defined below
    rules=(only_desired_sessions,only_one_session,no_oversuscribed_sessions)

    # combine them in one formula
    out=[]
    for rule in rules: out+=rule(student_preferences, session_capacities)
    return out

def only_desired_sessions(prefs, caps):
    """
    RULE 1. Builds CNF rule based on students' preferences for their sessions. 
    """
    return [
            [(stud+'_'+p, True) for p in pref]
            for stud, pref in prefs.items()]
     
def combos(array,n=2):
    """
    Given an array, returns a set of all unique N-long combinations
    of its elements. 
    """    
    # base case
    if n==0:
        yield frozenset()
        return

    # core recursion
    for c in set(combos(array,n-1)):
        for i in array:
            #added this to avoid duplicate combos
            if i not in c:
                # add element i to combo c
                yield frozenset({i})| c

def only_one_session(prefs, caps):
    """
    RULE 2. Returns a CNF formula that represent the rule for which
    each student can be assigned to at most one session. 
    """
    rooms = tuple(caps.keys())
    # for any pair of sessions, each student can only be in one session
    return [
            [('%s_%s' % (stud,r1), False),
             ('%s_%s' % (stud,r2), False)]
            for stud in prefs 
            for r1,r2 in combos(rooms)]

def no_oversuscribed_sessions(prefs, caps):
    """
    RULE 3. Returns a CNF formula stating that no session should be oversuscribed
    """
    out = []
    for room, cap in caps.items():
        # if room capacity > num students, go to next room 
        # since this one is safely undersuscribed
        if cap >= len(prefs):
            continue
        # if a room contains N students, then in every group of N+1 students 
        # there must be a student not in that session
        stud_combos = combos(prefs, cap+1)
        for group in stud_combos:
            out.append([('%s_%s' % (stud, room), False) for stud in group])
    return out

if __name__ == '__main__':
    import doctest
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)
