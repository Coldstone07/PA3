from mcts_node import MCTSNode
from random import choice
from math import sqrt, log

num_nodes = 1000
explore_faction = 2.


def traverse_nodes(node, board, state, identity):
    """ Traverses the tree until the end criterion are met.

    Args:
        node:       A tree node from which the search is traversing.
        board:      The game setup.
        state:      The state of the game.
        identity:   The bot's identity, either 'red' or 'blue'.

    Returns:        A node from which the next stage of the search can proceed.

    """

    # do Upper Confidence Bounds for Trees to find the proper leaf node
    if node.child_nodes:  # check if current node has children
        UCB = dict()  # dict of upper confidence bound
        for child in node.child_nodes.values():
            # do the formula
            exploit = child.wins / child.visits if child.visits != 0 else 0
            explore = 2 * sqrt(log(node.visits) / child.visits) if child.visits != 0 else 0
            UCB[child] = exploit + explore
            if UCB[child] == 0:
                return child
        print("Printing the dictionary: ", UCB.keys(), UCB.values())

        highestChild = max(UCB, key=UCB.get)
    else:
        return node

    if highestChild.untried_actions:
        leaf_node = highestChild
    else:
        if highestChild.child_nodes:
            leaf_node = traverse_nodes(highestChild, board, state, identity)
        else:
            leaf_node = highestChild
    return leaf_node
    # for the nodes with the highest Upper Confidenc Bound
    # if untried action, then return it

    # if no untried actions and have a child then go to the child
    # return traverse_nodes(child_node, board, state, identity) - would look something like this
    # if no untried actions and no children then reutrn
    pass

    # Hint: return leaf_node


def expand_leaf(node, board, state):
    """ Adds a new leaf to the tree by creating a new child node for the given node.

    Args:
        node:   The node for which a child will be added.
        board:  The game setup.
        state:  The state of the game.

    Returns:    The added child node.

    """
    print("State: ", state)
    action = node.untried_actions.pop()
    state = board.next_state(state, action)
    print("Updated state: ", state)
    child = MCTSNode(parent=node, parent_action=action, action_list=board.legal_actions(state))
    node.child_nodes[action] = child
    child.parent = node

    # add  parent actions to child node's action
    # add stuff to mcts_node parent actions

    # temp return
    return child, state
    pass
    # Hint: return new_node


def rollout(board, state):
    """ Given the state of the game, the rollout plays out the remainder randomly.

    Args:
        board:  The game setup.
        state:  The state of the game.

    """
    while not state.is_ended:
        next_move = choice(board.legal_actions(state))
        state = board.next_state(state, next_move)
    # at the end
    return board.win_values(state)
    pass


def backpropagate(node, won):
    """ Navigates the tree from a leaf node to the root, updating the win and visit count of each node along the path.

    Args:
        node:   A leaf node.
        won:    An indicator of whether the bot won or lost the game.

    """
    # updateing visit and wins until we reach root node aka no parents
    leaf = node
    while leaf.parent_action is not None:
        leaf.visits = leaf.visits + 1
        if won is 1:
            leaf.wins = leaf.wins + 1
        leaf = leaf.parent
    pass


def think(board, state):
    """ Performs MCTS by sampling games and calling the appropriate functions to construct the game tree.

    Args:
        board:  The game setup.
        state:  The state of the game.

    Returns:    The action to be taken.

    """
    identity_of_bot = board.current_player(state)
    root_node = MCTSNode(parent=None, parent_action=None, action_list=board.legal_actions(state))
    # print("Board: ", board, "State: ", state)
    for step in range(num_nodes):
        # Copy the game for sampling a playthrough
        sampled_game = state

        # Start at root
        node = root_node

        # Do MCTS - This is all you!
        parent_node = traverse_nodes(node, board, sampled_game, identity_of_bot)
        child_node, next_state = expand_leaf(parent_node, board, state)
        num = rollout(board, next_state)  # result of game who won -1 = lose
        my_value = num[identity_of_bot]
        backpropagate(child_node, my_value)
    # Return an action, typically the most frequently used action (from the root) or the action with the best
    # estimated win rate.
    winRatio = []
    for child in root_node.child_nodes:
        winRatio.append((child, child.wins / child.visits))
    best_child = max(winRatio, key=lambda i: i[1])[0]
    # find the best child with win/visits
    # return child.parent_action
    return best_child.parent_action
