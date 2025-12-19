import abc


class Tickable(abc.ABC):

    def tick(self, dt_s: float) -> dict:
        pass
