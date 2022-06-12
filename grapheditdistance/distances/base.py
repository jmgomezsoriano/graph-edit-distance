from abc import ABCMeta, ABC, abstractmethod
from typing import List, Tuple, Sequence, Any, Hashable

from grapheditdistance.base import BaseGraph
from grapheditdistance.operators import Operator


class EditDistance(ABC):
    __metaclass__ = ABCMeta

    def weights(self,
                prev_value: Any,
                curr_value: Any,
                pos: int,
                entities: Sequence) -> List[Tuple[str, float]]:
        return [('default', 1.)]

    @abstractmethod
    def costs(self,
              pos: int,
              entity: Sequence[Hashable],
              graph: BaseGraph,
              curr_node: int,
              next_node: int) -> List[Operator]:
        pass
