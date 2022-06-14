from abc import ABCMeta, ABC, abstractmethod
from typing import Any, List

from grapheditdistance import FINAL_NODE


class Operator(ABC):
    """ Abstract operator. """
    __metaclass__ = ABCMeta

    @property
    def name(self) -> str:
        """
        :return: The operator name.
        """
        return self._name

    @property
    def cost(self) -> float:
        """
        :return: The operator cost.
        """
        return self._cost

    @property
    def increase_pos(self) -> int:
        """
        :return: The position increment.
        """
        return self._increase_pos

    @property
    def next_node(self) -> int:
        """
        :return: The next node.
        """
        return self._next_node

    def __init__(self, name: str, cost: float, increase_pos: int, next_node: int) -> None:
        """ Constructor.

        :param name: The operator name.
        :param cost: The operator cost.
        :param increase_pos: The position increment in the entity.
        :param next_node: The next node to jump.
        """
        self._name = name
        self._cost = cost
        self._increase_pos = increase_pos
        self._next_node = next_node

    def __repr__(self) -> str:
        """ A representation of this operator. """
        return f'({self.name}, {self.cost})'

    def __str__(self) -> str:
        """ The name of the operator. """
        return repr(self) + f'->{self.next_node}'

    def __hash__(self) -> int:
        """ Create a hash of this operator .

        :return: An integer that represents the hash.
        """
        return hash(str(self))

    def __eq__(self, other: 'Operator') -> bool:
        """ Compare two operators.

        :param other: Other operator.
        :return: True if this the same operator, with the same elements, and the same cost.
        """
        return str(self) == str(other)

    @abstractmethod
    def operate(self) -> List[Any]:
        """ Apply the operation adn return the list of modified elements. """
        pass


class NoneOperator(Operator):
    """ A dummy operator that do nothing. """
    @property
    def element(self) -> Any:
        """ The element of the entity to do nothing. """
        return self._element

    def __init__(self, element: Any, next_node: int) -> None:
        """ Constructor.

        :param element: The current element.
        :param next_node: The next node.
        """
        super().__init__('None', 0, 1, next_node)
        self._element = element

    def __repr__(self) -> str:
        """ A representation of this operator. """
        return f'({self.name})'

    def operate(self) -> List[Any]:
        """
        :return: The same element without changes.
        """
        return [self.element]


class FinalOperator(Operator):
    """ An operator to indicate that this is the last. """
    def __init__(self) -> None:
        """ Constructor. """
        super().__init__('Final', 0, 0, FINAL_NODE)

    def __repr__(self) -> str:
        """ A representation of this operator. """
        return f'({self.name})'

    def operate(self) -> List[Any]:
        """
        :return: The empty element.
        """
        return []


class InsertOperator(Operator):
    """ The insert operation. """
    @property
    def inserted_element(self) -> Any:
        """
        :return: The inserted element.
        """
        return self._element

    def __init__(self, cost: float, element: Any, curr_node: int) -> None:
        """ Constructor.
        :param cost: The insertion cost.
        :param element: The element to insert.
        :param curr_node: The current node.
        """
        super().__init__('insert', cost, 1, curr_node)
        self._element = element

    def __repr__(self) -> str:
        """ A representation of this operator. """
        return f'({self.name}[{self.inserted_element}], {self.cost})'

    def operate(self) -> List[Any]:
        """
        :return: An empty entity because it is necessary to remove the inserted element.
        """
        return []


class DeleteOperator(Operator):
    """ The delete operation. """
    @property
    def deleted_element(self) -> Any:
        """
        :return: The deleted element.
        """
        return self._element

    def __init__(self, cost: float, element: Any, next_node: int) -> None:
        """ Constructor.
        :param cost: The deletion cost.
        :param element: The element to delete.
        :param next_node: The next node.
        """
        super().__init__('delete', cost, 0, next_node)
        self._element = element

    def __repr__(self) -> str:
        """ A representation of this operator. """
        return f'({self.name}[{self.deleted_element}], {self.cost})'

    def operate(self) -> List[Any]:
        """
        :return: The deleted element.
        """
        return [self._element]


class ReplaceOperator(Operator):
    """ The replace operation. """
    @property
    def from_element(self) -> Any:
        """
        :return: The element to replace.
        """
        return self._from_element

    @property
    def to_element(self) -> Any:
        """
        :return: The element to replace with.
        """
        return self._to_element

    def __init__(self, cost: float, from_element: Any, to_element: Any, next_node: int) -> None:
        """ Constructor.
        :param cost: The insertion cost.
        :param from_element: The element to replace.
        :param to_element: The element to replace with.
        :param next_node: The current node.
        """
        super().__init__('replace', cost, 1, next_node)
        self._from_element = from_element
        self._to_element = to_element

    def __repr__(self) -> str:
        """ A representation of this operator. """
        return f'({self.name}[{self.from_element} -> {self.to_element}], {self.cost})'

    def operate(self) -> List[Any]:
        """
        :return: the element which is necessary to replace with.
        """
        return [self.to_element]
