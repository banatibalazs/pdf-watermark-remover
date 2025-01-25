# interfaces/image_displayer_interface.py
from abc import ABC, abstractmethod

class ImageDisplayerInterface(ABC):
    @abstractmethod
    def display_image(self, mask):
        pass

    @abstractmethod
    def toggle_text(self):
        pass

    @abstractmethod
    def next_page(self):
        pass

    @abstractmethod
    def previous_page(self):
        pass