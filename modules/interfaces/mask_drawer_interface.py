# interfaces/mask_drawer_interface.py
from abc import ABC, abstractmethod

class MaskDrawerInterface(ABC):
    @abstractmethod
    def draw_free(self, event, x, y, flags, param):
        pass

    @abstractmethod
    def reset_mask(self):
        pass

    @abstractmethod
    def get_gray_mask(self):
        pass