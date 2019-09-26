import adtrees as adt
import time


def trees():
    names = ['random1.xml', 'random2.xml']
    for i in range(1, 4):
        names.append("synthetic" + str(i) + ".xml")
    return names


def all_opp_strats(tree):
    '''
    create all opponent's strategies in the tree 'tree'
    '''
    attackers_actions = tree.basic_actions('a')
    defenders_actions = tree.basic_actions('d')
    oppStrats = adt.attribute_domain.AttrDomain(adt.utils.oplushat, adt.utils.oplushat,
                                                adt.utils.oplushat, adt.utils.otimes, adt.utils.oplushat, adt.utils.oplushat)
    ba = adt.basic_assignment.BasicAssignment()
    for b in attackers_actions:
        ba[b] = []
    for b in defenders_actions:
        ba[b] = [[b]]
    result = oppStrats.evaluateBU(tree, ba)
    # removing duplicates
    res = []
    for item in result:
        if item not in res:
            res.append(item)
    # don't forget the empty strategy
    res.append([])
    return res


def main():
    for name in trees():
        # 1. load tree
        T = adt.ADTree(path=name)
        # 2. get params
        # number of nodes in DAG representation
        nodes_in_dag = 0
        unique_labels = []
        for node in T.dict:
            if node.label not in unique_labels:
                unique_labels.append(node.label)
                nodes_in_dag += 1
        # number of basic actions of the proponent
        bap = len(T.basic_actions('a'))
        # number of basic actions of the opponent
        bop = len(T.basic_actions('d'))
        # number of opponent's strategies
        oppstr = len(all_opp_strats(T))
        print("file name:", name)
        print("number of nodes:", nodes_in_dag)
        print("number of basic actions of the proponent:", bap)
        print("number of basic actions of the opponent:", bop)
        # the following will display some additional parameters
        def_sem = def_sem_feedback(T)
        print("size of defense semantics: " + str(len(def_sem)))
        print()
    return


def def_sem_feedback(tree):
    """
    Return the defense semantics of an attack-defense tree T.

    Returns a list of two-element lists
        [[set, set], [set, set], ..., [set, set]],
    with each element of each of the lists being a set of basic actions.

    Provides some feedback.
    """
    attackers_actions = tree.basic_actions('a')
    defenders_actions = tree.basic_actions('d')
    # step 1: create proponent's strategies
    ba = adt.basic_assignment.BasicAssignment()
    for b in attackers_actions:
        ba[b] = []
    for b in defenders_actions:
        ba[b] = [[b]]
    # substep 1.1: create witnesses
    witnesses = adt.default_domains.suffWit.evaluateBU(tree, ba)
    # don't forget the empty defense strategy
    witnesses.append([])
    print("number of all opponent's strategies: " +
          str(len(all_opp_strats(tree))))
    print('number of witnesses obtained via SuffWit: ' + str(len(witnesses)))
    # substep 1.2: iterate over witnesses, get corresponding proponent's strategies
    # countering them
    AS = []
    for witness in witnesses:
        ba = adt.basic_assignment.BasicAssignment()
        for b in attackers_actions:
            ba[b] = [[b]]
        for b in defenders_actions:
            if b in witness:
                ba[b] = []
            else:
                ba[b] = [[]]
        candidates = adt.default_domains.countStrats.evaluateBU(tree, ba)
        # select the minimal ones
        for AS_countering_witness in adt.utils.minimal_lists(candidates):
            if AS_countering_witness not in AS:
                AS.append(AS_countering_witness)
    print("number of proponent's strategies: " + str(len(AS)))

    # At this point AS is the set of all attack strategies in the tree.
    # step 2: opponent's strategies countering proponent's strategies
    result = []
    # 2.1 swap actors
    proponent = 'd'
    # 2.2 create a basic assignment
    for b in tree.basic_actions('d'):
        ba[b] = [[b]]
    # iterate
    for A in AS:
        # modify the basic assignment
        for b in attackers_actions:
            if b in A:
                ba[b] = []
            else:
                ba[b] = [[]]
        # do the bottom-up
        candidates = adt.default_domains.countStrats.evaluateBU(
            tree, ba, proponent)
        # select the minimal ones
        for candidate in adt.utils.minimal_lists(candidates):
            result.append([set(A), set(candidate)])
    return result

if __name__ == '__main__':
    main()
