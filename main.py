#!/usr/bin/env python
from functools import reduce
from typing import Tuple
from typing import List
from typing import Dict
from typing import Optional
from typing import TypeVar
from typing import Callable

from mypy_extensions import TypedDict
import pulp
import yaml


class Vote(TypedDict):
    is_new: Optional[bool]
    is_teacher: Optional[bool]
    score: int


Games = Dict[str, Vote]


with open(r'./games.yaml') as game_file, open(r'./votes.yaml') as vote_file:
    GAMES: Dict[str, List[int]] = yaml.full_load(game_file)
    VOTES: Dict[str, Games] = yaml.full_load(vote_file)


def main():
    player_names = list(VOTES.keys())
    table_permutations = pulp.allcombinations(player_names, len(player_names))
    possible_setups = flatmap(mapper, table_permutations)
    possible_setups = list(filter(is_teachable, possible_setups))
    included = pulp.LpVariable.dicts('Included setups',
                                     possible_setups,
                                     0,
                                     1,
                                     pulp.LpInteger)
    problem = pulp.LpProblem('Game Seating Problem', pulp.LpMaximize)
    problem += pulp.lpSum([objective(setup) * included[setup]
                           for setup in possible_setups])
    for player in player_names:
        problem += pulp.lpSum([included[setup]
                               for setup in possible_setups
                               if player in setup]) == 1, f"Must seat {player}"
    problem.solve()
    print([(objective(setup), *setup)
           for setup in possible_setups
           if included[setup].value() == 1])


T = TypeVar('T')
U = TypeVar('U')
def flatmap(f: Callable[[T], List[U]], xs: List[T]) -> List[U]:
    l: List[U] = []
    for x in xs:
        l += f(x)
    return l


def is_teachable(setup: Tuple[str, ...]) -> bool:
    (game, *players) = setup
    new_players = [VOTES[p].get(game, {}).get('is_new', False) for p in players]
    if not any(new_players):
        return True
    teachers = [VOTES[p].get(game, {}).get('is_teacher', False) for p in players]
    if any(new_players) and any(teachers):
        return True
    return False


def mapper(table: Tuple[str, ...]) -> List[Tuple[str, ...]]:
    return [(game, *table)
            for game, counts in GAMES.items()
            if len(table) in counts]


def objective(setup: Tuple[str, ...]) -> int:
    (game, *players) = setup
    return reduce(lambda s, p: s + VOTES[p].get(game, {}).get('score', 0),
                  players,
                  0)


if __name__ == '__main__':
    main()
