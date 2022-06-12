from grapheditdistance.base import BaseGraph
from grapheditdistance.distances import EditDistance
from typing import Sequence, List, Hashable

from grapheditdistance.operators import Operator, NoneOperator, ReplaceOperator, DeleteOperator, InsertOperator


class Levenshtein(EditDistance):
    def __init__(self, insert_cost: float = 1, delete_cost: float = 1, replace_cost: float = 1) -> None:
        self.insert_cost = insert_cost
        self.delete_cost = delete_cost
        self.replace_cost = replace_cost

    def costs(self,
              pos: int,
              entity: Sequence[Hashable],
              graph: BaseGraph,
              curr_node: int,
              next_node: int) -> List[Operator]:
        operators = []
        next_value = graph.value(next_node)
        if pos < len(entity):
            curr_value = entity[pos]
            if curr_value == next_value:
                operators.append(NoneOperator(curr_value, next_node))
            elif next_value != '_$_':
                operators.append(ReplaceOperator(self.replace_cost, curr_value, next_value, next_node))
            operators.append(InsertOperator(self.insert_cost, curr_value, curr_node))
        if next_value != '_$_':
            operators.append(DeleteOperator(self.delete_cost, next_value, next_node))
        return operators
