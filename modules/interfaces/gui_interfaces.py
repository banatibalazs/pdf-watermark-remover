# modules/interfaces/display_interface.py
from abc import ABC, abstractmethod


class DisplayInterface(ABC):
    @abstractmethod
    def display_image(self, *args, **kwargs):
        pass

    @abstractmethod
    def close_window(self):
        pass

    @abstractmethod
    def change_window_setup(self, *args, **kwargs):
        pass

    @abstractmethod
    def set_texts(self, texts, text_color, title):
        pass

    @abstractmethod
    def start_main_loop(self):
        pass

    def update_trackbars(self, current_parameters):
        pass


class KeyHandlerInterface(ABC):
    @abstractmethod
    def handle_key(self, key) -> bool:
        pass


class MouseHandlerInterface(ABC):
    @abstractmethod
    def handle_mouse(self, event) -> None:
        pass