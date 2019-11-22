#!/usr/bin/env python
from functools import reduce

import pulp


GAMES = {
    'scythe': [3, 4, 5, 6],
    'viticulture': [3, 4, 5],
    'spirit island': [3],
    'cosmic encounter': [4, 5, 6],
    'welcome to': [3, 4, 5, 6],
    'sushi go party': [3, 4, 5, 6, 7],
    'one night ultimate werewolf': [5, 6, 7, 8, 9, 10],
    'skull': [4, 5, 6],
    'junk art': [3, 4, 5, 6],
    'no thanks': [3, 4, 5],
    'coup': [4, 5, 6],
    'race for the galaxy': [3, 4, 5],
}

PLAYERS = {
    'nicholas': {
        'scythe': 3,
        'viticulture': 2,
        'cosmic encounter': 3,
        'welcome to': 1,
        'sushi go party': 2,
        'one night ultimate werewolf': 2,
        'skull': 0,
        'junk art': 1,
        'no thanks': 2,
        'coup': 2,
        'race for the galaxy': 2,
    },
    'shayle': {
        'scythe': 2,
        'viticulture': 2,
        'cosmic encounter': 3,
        'welcome to': 1,
        'sushi go party': 3,
        'one night ultimate werewolf': 0,
        'skull': 2,
        'junk art': 2,
        'no thanks': 3,
        'coup': 3,
        'race for the galaxy': 0,
    },
    'yousaf': {
        'scythe': 0,
        'viticulture': 0,
        'cosmic encounter': 0,
        'welcome to': 0,
        'sushi go party': 3,
        'one night ultimate werewolf': 0,
        'skull': 0,
        'junk art': 3,
        'no thanks': 0,
        'coup': 0,
        'race for the galaxy': 0,
    },
    'dylan': {
        'scythe': 3,
        'viticulture': 1,
        'cosmic encounter': 3,
        'welcome to': 2,
        'sushi go party': 2,
        'one night ultimate werewolf': 1,
        'skull': 1,
        'junk art': 3,
        'no thanks': 2,
        'coup': 2,
        'race for the galaxy': 2,
    },
    'greg': {
        'scythe': 0,
        'viticulture': 0,
        'cosmic encounter': 3,
        'welcome to': 1,
        'sushi go party': 1,
        'one night ultimate werewolf': 2,
        'skull': 1,
        'junk art': 2,
        'no thanks': 1,
        'coup': 2,
        'race for the galaxy': 1,
    },
}


def main():
    player_names = list(PLAYERS.keys())
    table_permutations = pulp.allcombinations(player_names, len(player_names))
    possible_setups = reduce(reducer, table_permutations, [])

    included = pulp.LpVariable.dicts(
        'Included setups',
        possible_setups,
        0,
        1,
        pulp.LpInteger,
    )
    problem = pulp.LpProblem('Game Seating Problem', pulp.LpMaximize)
    problem += pulp.lpSum([objective(setup) * included[setup]
                           for setup in possible_setups])
    for player in player_names:
        problem += pulp.lpSum([included[setup]
                               for setup in possible_setups
                               if player in setup]) == 1, f"Must seat {player}"

    problem.solve()

    return [(objective(setup), *setup)
            for setup in possible_setups
            if included[setup].value() == 1]

def reducer(l, table):
    for game, counts in GAMES.items():
        if len(table) in counts:
            l.append((game, *table))
    return l

def objective(t):
    game = t[0]
    players = t[1:]
    return reduce(lambda s, p: s + PLAYERS[p].get(game, 0), players, 0)

if __name__ == '__main__':
    print(main())
