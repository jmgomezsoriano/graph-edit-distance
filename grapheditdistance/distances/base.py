from abc import ABCMeta, ABC
from typing import List, Tuple, Sequence, Any


class EditDistance(ABC):
    __metaclass__ = ABCMeta

    def weights(self,
                prev_value: Any,
                curr_value: Any,
                next_value: Any,
                pos: int,
                entity: Sequence) -> List[Tuple[str, float]]:
        return [('default', 1.)]
