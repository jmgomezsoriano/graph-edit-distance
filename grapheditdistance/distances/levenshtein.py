from grapheditdistance import FINAL_NODE
from grapheditdistance.base import BaseGraph
from grapheditdistance.distances import EditDistance
from typing import Sequence, List, Hashable, Any

from grapheditdistance.operators import Operator, NoneOperator, ReplaceOperator, DeleteOperator, InsertOperator, \
    FinalOperator


def same_inserted(operator: Operator, element: Any) -> bool:
    return isinstance(operator, InsertOperator) and operator.inserted_element == element


def same_deleted(operator: Operator, element: Any) -> bool:
    return isinstance(operator, DeleteOperator) and operator.deleted_element == element


class Levenshtein(EditDistance):
    @property
    def max_cost(self):
        return max([self.insert_cost, self.delete_cost, self.replace_cost])

    def __init__(self, insert_cost: float = 1, delete_cost: float = 1, replace_cost: float = 1) -> None:
        self.insert_cost = insert_cost
        self.delete_cost = delete_cost
        self.replace_cost = replace_cost

    def costs(self,
              pos: int,
              entity: Sequence[Hashable],
              graph: BaseGraph,
              curr_node: int,
              next_node: int,
              operators) -> List[Operator]:
        new_operators = []
        if next_node == FINAL_NODE and pos == len(entity):
            new_operators.append(FinalOperator())
        else:
            next_value = graph.value(next_node)
            if pos < len(entity):
                curr_value = entity[pos]
                if curr_value == next_value:
                    new_operators.append(NoneOperator(curr_value, next_node))
                elif next_node != FINAL_NODE:
                    new_operators.append(ReplaceOperator(self.replace_cost, curr_value, next_value, next_node))
                # If the previous operator was the same deleted element, give the maximum value
                weight = self.max_cost * len(entity) if operators and same_deleted(operators[-1], curr_value) else self.insert_cost
                new_operators.append(InsertOperator(weight, curr_value, curr_node))
            if next_node != FINAL_NODE:
                # If the previous operator was the same inserted element, give the maximum value
                weight = self.max_cost * len(entity) if operators and same_inserted(operators[-1], next_value) else self.delete_cost
                new_operators.append(DeleteOperator(weight, next_value, next_node))
        return new_operators

    # def _was_the_same_element(self, operators: List[Operator], cls: operator: Operator, element: Any) -> bool:
    #     if operators:
    #
    #     else:
    #         return False

