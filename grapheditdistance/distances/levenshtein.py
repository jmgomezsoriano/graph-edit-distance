from grapheditdistance import FINAL_NODE
from grapheditdistance.base import BaseGraph
from grapheditdistance.distances import EditDistance
from typing import Sequence, List, Hashable, Any

from grapheditdistance.operators import Operator, NoneOperator, ReplaceOperator, DeleteOperator, InsertOperator, \
    FinalOperator


class Levenshtein(EditDistance):
    """ Implements the edit distances methods for the Levenshtein algorithm. """
    @property
    def max_cost(self):
        """
        :return: The maximum cost.
        """
        return self._max_cost

    def __init__(self, insert_cost: float = 1, delete_cost: float = 1, replace_cost: float = 1) -> None:
        """ Constructor from the different costs.

        :param insert_cost: The cost to insert an element.
        :param delete_cost: The cost to delete an element.
        :param replace_cost: The cost to replace an element by other one.
        """
        self._insert_cost = insert_cost
        self._delete_cost = delete_cost
        self._replace_cost = replace_cost
        self._max_cost = max([self._insert_cost, self._delete_cost, self._replace_cost])

    def insert_cost(self, element: Any) -> float:
        """ Calculate the insertion cost.

        :param element: The element to insert.
        :return: The operator cost.
        """
        return self._insert_cost

    def delete_cost(self, element: Any) -> float:
        """ Calculate the deletion cost.

        :param element: The element to remove.
        :return: The operator cost.
        """
        return self._delete_cost

    def replace_cost(self, fr: Any, to: Any) -> float:
        """ Calculate the replacement cost.

        :param fr: The element to replace from.
        :param to: The element to replace with.
        :return: The operator cost.
        """
        return self._replace_cost

    def costs(self,
              pos: int,
              entity: Sequence[Hashable],
              graph: BaseGraph,
              curr_node: int,
              next_node: int,
              operators) -> List[Operator]:
        """ This method should return a list of operators with the different costs of each operation.

        :param pos: The current position of the entity.
        :param entity: The entity is a sequence of hashable elements
        :param graph: The graph.
        :param curr_node: The current node.
        :param next_node: The next node.
        :param operators: The list of operators to arrive to the current node.
        :return: The different operators to explore and add to the previous list of operators.
        """
        new_operators = []
        # If the node is the final one and the position is at the end of the entity, add a final operator.
        if next_node == FINAL_NODE and pos == len(entity):
            new_operators.append(FinalOperator())
        else:
            # Get the next value from the next node
            next_value = graph.value(next_node)
            # If the position is less than the entity length, add all the operators.
            if pos < len(entity):
                curr_value = entity[pos]
                if curr_value == next_value:
                    new_operators.append(NoneOperator(curr_value, next_node))
                elif next_node != FINAL_NODE:
                    cost = self.replace_cost(curr_value, next_value)
                    new_operators.append(ReplaceOperator(cost, curr_value, next_value, next_node))
                # If the previous operator was the same deleted element, give the maximum value to avoid this path
                weight = self._calculate_insert_cost(entity, operators, curr_value)
                new_operators.append(InsertOperator(weight, curr_value, curr_node))
            if next_node != FINAL_NODE:
                # If the previous operator was the same inserted element, give the maximum value to avoid this path
                weight = self._calculate_delete_cost(entity, operators, next_value)
                new_operators.append(DeleteOperator(weight, next_value, next_node))
        return new_operators

    def _calculate_insert_cost(self, entity: Sequence[Hashable], operators: List[Operator], value: Hashable) -> float:
        """ Calculate the final insert operation cost depending on if the previous operator is the
           opposite one (a delete operation) with the same element.

        :param entity: The full entity.
        :param operators: The list of operators to this position.
        :param value: The value to compare with.
        :return: True if the previous operator is the opposite one with the same element value.
        """
        if operators and isinstance(operators[-1], DeleteOperator) and operators[-1].deleted_element == value:
            return self.max_cost * len(entity)
        else:
            return self.insert_cost(value)

    def _calculate_delete_cost(self, entity: Sequence[Hashable], operators: List[Operator], value: Hashable) -> float:
        """ Calculate the final insert operation cost depending on if the previous operator is the
           opposite one (an insert operation) with the same element.

        :param entity: The full entity.
        :param operators: The list of operators to this position.
        :param value: The value to compare with.
        :return: True if the previous operator is the opposite one with the same element value.
        """
        if operators and isinstance(operators[-1], InsertOperator) and operators[-1].inserted_element == value:
            return self.max_cost * len(entity)
        else:
            return self.delete_cost(value)


class WeightedLevenshtein(Levenshtein):
    """ A weighted levenshtein algorithm which allows to define different costs to operate with different elements.
    For example, if you want that to the default cost for insert, delete and replace an element is 1.0, 0.9 and 0.8,
    respectively, but if you insert or delete a space their costs will be 0.1 and 0.2, respectively, and
    to replace one 'e' by a 'c', you can do the following::

        lev = WeightedLevenshtein(1, 0.9, 0.8)
        lev.add_insert_cost(' ', 0.1)
        lev.add_delete_cost(' ', 0.2)
        lev.add_replace_cost('e', 'c, 0.5)

    """
    @property
    def max_cost(self):
        """
        :return: The maximum cost.
        """
        return self._max_cost

    def __init__(self, insert_cost: float = 1, delete_cost: float = 1, replace_cost: float = 1) -> None:
        """ Constructor from the different costs.

        :param insert_cost: The default cost to insert an element.
        :param delete_cost: The default cost to delete an element.
        :param replace_cost: The default cost to replace an element by other one.
        """
        super().__init__(insert_cost, delete_cost, replace_cost)
        self._max_cost = max([self._insert_cost, self._delete_cost, self._replace_cost])
        self._custom_insert_costs = {}
        self._custom_delete_costs = {}
        self._custom_replace_costs = {}

    def add_insert_cost(self, element: Any, cost: float) -> None:
        """ Add an insertion cost for a specific inserted element.

        :param element: The element to insert.
        :param cost: The cost of inserting that element.
        """
        self._custom_insert_costs[element] = cost
        self._max_cost = max([cost, self._max_cost])

    def add_delete_cost(self, element: Any, cost: float) -> None:
        """ Add a deletion cost for a specific deleted element.

        :param element: The element to delete.
        :param cost: The cost of deleting that element.
        """
        self._custom_delete_costs[element] = cost
        self._max_cost = max([cost, self._max_cost])

    def add_replace_cost(self, fr: Any, to: Any, cost: float) -> None:
        """ Add a replacement cost for a specific replace rule.

        :param fr: The element to replace for.
        :param to: The element to replace with.
        :param cost: The cost of replace "fr" by "to" elements.
        """
        self._custom_replace_costs[(fr, to)] = cost
        self._max_cost = max([cost, self._max_cost])

    def insert_cost(self, element: Any) -> float:
        """ Calculate the insertion cost.

        :param element: The element to insert.
        :return: The operator cost.
        """
        return self._custom_insert_costs.get(element, self._insert_cost)

    def delete_cost(self, element: Any) -> float:
        """ Calculate the deletion cost.

        :param element: The element to remove.
        :return: The operator cost.
        """
        return self._custom_delete_costs.get(element, self._delete_cost)

    def replace_cost(self, fr: Any, to: Any) -> float:
        """ Calculate the replacement cost.

        :param fr: The element to replace from.
        :param to: The element to replace with.
        :return: The operator cost.
        """
        return self._custom_replace_costs.get((fr, to), self._replace_cost)
