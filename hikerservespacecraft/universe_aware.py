from typing import Dict, Any


class UniverseAware:
    """
    A class that represents an entity aware of its universe context.
    """

    def __init__(self, universe: Dict[str, Any]):
        """
        Initialize the UniverseAware instance with a universe context.

        :param universe: The universe context to be associated with this instance.
        """
        self.universe: Dict[str, Any] = universe

    def get_universe(self) -> Dict[str, Any]:
        """
        Retrieve the universe context associated with this instance.

        :return: The universe context.
        """
        return self.universe

    def set_universe(self, universe: Dict[str, Any]):
        """
        Set or update the universe context for this instance.

        :param universe: The new universe context to be associated with this instance.
        """
        self.universe = universe
