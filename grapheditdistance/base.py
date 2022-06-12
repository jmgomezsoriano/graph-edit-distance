from abc import ABC, ABCMeta, abstractmethod
from typing import Hashable, Sequence, Iterable, List

from networkx.classes.reportviews import NodeView

VALUE, NEIGHBORS, WEIGHT = 'value', 'neighbors', 'weight'


class BaseGraph(ABC):
    __metaclass__ = ABCMeta

    @property
    @abstractmethod
    def nodes(self) -> NodeView:
        pass

    def neighbors(self, node: int) -> dict:
        return self.nodes[node][NEIGHBORS]

    def get_neighbor(self, value: Hashable, node: int, default: int = None) -> int:
        return self.neighbors(node).get(value, default)

    def set_neighbor(self, prev_node: int, node: int, value: Hashable) -> None:
        self.neighbors(prev_node)[value] = node

    @abstractmethod
    def add(self, entity: Sequence[Hashable]) -> None:
        pass

    def preprocess(self, value: Sequence[Hashable]) -> Sequence[Hashable]:
        return value

    def index(self, entities: Iterable[Sequence[Hashable]]) -> None:
        for entity in entities:
            self.add(entity)

    @abstractmethod
    def draw(self, edge_labels: bool = False) -> None:
        pass

    @abstractmethod
    def adjacent(self, node: int) -> Iterable[int]:
        pass

    @abstractmethod
    def value(self, node: int) -> Hashable:
        pass

    @abstractmethod
    def seq_search(self, entity: Sequence[Hashable], threshold: float = 0.8, nbest: int = 1) -> List[tuple]:
        pass
