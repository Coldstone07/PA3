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

    if node.untried_actions:
        return node, 1, state
    else:  # if no untried action
        if node.child_nodes:  # check if current node has children
            prev_player = board.previous_player(state)
            UCB = dict()  # dict of upper confidence bound
            for child in node.child_nodes.values():  # do Upper Confidence Bounds for Trees to find the proper leaf nod
                exploit = child.wins / child.visits
                explore = explore_faction * sqrt(log(node.visits) / child.visits)
                if board.current_player(state) == identity:  # we want to win so exploit to win
                    UCB[child] = exploit + explore
                else:  # we want to not win
                    UCB[child] = (1 - exploit) + explore
            # print("Printing the dictionary: ", UCB.keys(), UCB.values())
            highestChild = max(UCB, key=UCB.get)
            # print("UCB:, ", UCB, "Highest Child: ", highestChild)
            state = board.next_state(state, highestChild.parent_action)
            return traverse_nodes(highestChild, board, state, prev_player)
        else:
            return node, 0, state
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
    action = choice(node.untried_actions)  # pick a random untried action
    node.untried_actions.remove(action)  # remove the chosen action, so there are no repeats
    state_updated = board.next_state(state, action)  # change the state with chosen action
    child = MCTSNode(parent=node, parent_action=action, action_list=board.legal_actions(state_updated))  # create new node to rep the game state
    node.child_nodes[action] = child  # adds the child to dic of child_nodes
    return child, state  # return new child and it's game state
    pass
    # Hint: return new_node


def rollout(board, state):
    """ Given the state of the game, the rollout plays out the remainder randomly.

    Args:
        board:  The game setup.
        state:  The state of the game.

    """
    while not board.is_ended(state):  # checks if the game is done
        next_move = choice(board.legal_actions(state))  # chooses a random action from avaiable actions
        state = board.next_state(state, next_move)  # updates the state as it chooses the action
    return board.win_values(state)  # return the game results
    pass


def backpropagate(node, won):
    """ Navigates the tree from a leaf node to the root, updating the win and visit count of each node along the path.

    Args:
        node:   A leaf node.
        won:    An indicator of whether the bot won or lost the game.

    """
    # updating visit and wins until we reach root node aka no parents
    leaf = node  # make a leaf pointer that would allow for us to go up the tree
    while leaf is not None:  # goes until there is no parent
        leaf.visits = leaf.visits + 1  # adds the number of visits
        leaf.wins = leaf.wins + won  # add the wins and ties
        leaf = leaf.parent  # changes pointer to be that of the parents
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
        parent_node, id_return, parent_state = traverse_nodes(node, board, sampled_game, identity_of_bot)
        if id_return == 0:  # if no unused action and no childen
            child_node = parent_node
            next_state = parent_state
        else:  # if unused action
            child_node, next_state = expand_leaf(parent_node, board, parent_state)
        num = rollout(board, next_state)  # result of game who won, tied and lose
        my_result = num[identity_of_bot]
        backpropagate(child_node, my_result)
    # Return an action, typically the most frequently used action (from the root) or the action with the best
    # estimated win rate.
    winRatio = []
    for child in root_node.child_nodes.values():
        winRatio.append((child, child.wins/child.visits))
    #print(winRatio)
    best_child = max(winRatio, key=lambda i: i[1])[0]
    # find the best child with win/visits
    # return child.parent_action
    # print("mcts vanilla picking: ", best_child.parent_action)
    return best_child.parent_action
