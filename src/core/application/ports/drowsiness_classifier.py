from abc import ABC, abstractmethod


class DrowsinessClassifierPort(ABC):
    """Port for sequence-based drowsiness classifier."""

    @abstractmethod
    def predict_proba(self, ear_sequence: list[float]) -> float:
        """Return probability in range [0.0, 1.0]."""
        pass
