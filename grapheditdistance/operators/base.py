from abc import ABCMeta, ABC, abstractmethod
from typing import Any, List


class Operator(ABC):
    __metaclass__= ABCMeta

    @property
    def name(self) -> str:
        return self._name

    @property
    def cost(self) -> float:
        return self._cost

    @property
    def encrease_pos(self) -> int:
        return self._increase_pos

    @property
    def next_node(self) -> int:
        return self._next_node

    def __init__(self, name: str, cost: float, increase_pos: int, next_node: int) -> None:
        self._name = name
        self._cost = cost
        self._increase_pos = increase_pos
        self._next_node = next_node

    def __repr__(self) -> str:
        return f'({str(self)}, {self.cost})'

    def __str__(self) -> str:
        return self.name

    @abstractmethod
    def operate(self) -> List[Any]:
        pass


class NoneOperator(Operator):
    @property
    def element(self) -> Any:
        return self._element

    def __init__(self, element: Any, next_node: int) -> None:
        super().__init__('None', 0, 1, next_node)
        self._element = element

    def __repr__(self) -> str:
        return f'({str(self)})'

    def operate(self) -> List[Any]:
        return [self.element]


class InsertOperator(Operator):
    @property
    def inserted_element(self) -> Any:
        return self._element

    def __init__(self, cost: float, element: Any, curr_node: int) -> None:
        super().__init__('insert', cost, 1, curr_node)
        self._element = element

    def __str__(self) -> str:
        return f'{self.name}[{self.inserted_element}]'

    def operate(self) -> List[Any]:
        return [self.inserted_element]


class DeleteOperator(Operator):
    @property
    def deleted_element(self) -> Any:
        return self._element

    def __init__(self, cost: float, element: Any, next_node: int) -> None:
        super().__init__('delete', cost, 0, next_node)
        self._element = element

    def __str__(self) -> str:
        return f'{self.name}[{self.deleted_element}]'

    def operate(self) -> List[Any]:
        return []


class ReplaceOperator(Operator):
    @property
    def from_entity(self) -> Any:
        return self._from_entity

    @property
    def to_element(self) -> Any:
        return self._to_element

    def __init__(self, cost: float, from_element: Any, to_element: Any, next_node: int) -> None:
        super().__init__('replace', cost, 1, next_node)
        self._from_entity = from_element
        self._to_element = to_element

    def __str__(self) -> str:
        return f'{self.name}[{self.from_entity} -> {self.to_element}]'

    def operate(self) -> List[Any]:
        return [self.to_element]
