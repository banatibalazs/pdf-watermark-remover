# interfaces/mask_selector_interface.py
from abc import ABC, abstractmethod

class MaskSelectorInterface(ABC):
    @abstractmethod
    def draw_mask(self):
        pass

    @abstractmethod
    def get_gray_mask(self):
        pass