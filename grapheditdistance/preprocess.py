from typing import Sequence, Hashable


def dummy_preprocess(entity: Sequence[Hashable]) -> Sequence[Hashable]:
    """ A dummy entity preprocessor. This only returns the same element as input.
    :param entity: The entity.
    :return: The same entity.
    """
    return entity
