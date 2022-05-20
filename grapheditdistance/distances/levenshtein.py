from graphdistance.distances import EditDistance
from typing import Any, Sequence


class Levenshtein(EditDistance):
    def __init__(self, insert_cost: float = 1, delete_cost: float = 1, replace_cost: float = 1) -> None:
        self.insert_cost = insert_cost
        self.delete_cost = delete_cost
        self.replace_cost = replace_cost

    def distance(self, prev: Any, curr: Any, next: Any, pos: int, entity: Sequence[Any]) -> float:
        return 1.
