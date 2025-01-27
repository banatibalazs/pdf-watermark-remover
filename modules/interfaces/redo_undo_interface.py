# modules/interfaces/redo_undo_interface.py
from abc import ABC, abstractmethod

class RedoUndoInterface(ABC):
    @abstractmethod
    def undo(self) -> None:
        pass

    @abstractmethod
    def redo(self) -> None:
        pass

    @abstractmethod
    def save_state(self) -> None:
        pass