#!/usr/bin/env python
from functools import reduce

import pulp
import yaml

with open(r'./games.yaml') as game_file, open(r'./votes.yaml') as vote_file:
    GAMES = yaml.full_load(game_file)
    VOTES = yaml.full_load(vote_file)

def main():
    player_names = list(VOTES.keys())
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
    return reduce(lambda s, p: s + VOTES[p].get(game, 0), players, 0)

if __name__ == '__main__':
    print(main())
