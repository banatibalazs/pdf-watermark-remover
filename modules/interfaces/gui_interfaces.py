# modules/interfaces/display_interface.py
from abc import ABC, abstractmethod


class DisplayInterface(ABC):
    @abstractmethod
    def display_image(self, *args, **kwargs):
        pass


class KeyHandlerInterface(ABC):
    @abstractmethod
    def handle_key(self, key):
        pass


class MouseHandlerInterface(ABC):
    @abstractmethod
    def handle_mouse(self, event, x, y, flags, param):
        pass