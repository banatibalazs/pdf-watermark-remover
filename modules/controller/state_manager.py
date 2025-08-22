# state_manager.py
import numpy as np
from typing import List


class MaskStateManager:
    def __init__(self, model):
        self.model = model

    def save_state(self) -> None:
        self.model.temp_mask = self.model.final_mask
        self.model.undo_stack.append(self.model.final_mask.copy())
        self.model.redo_stack.clear()

    def undo(self) -> None:
        if not self.model.undo_stack:
            return
        self.model.redo_stack.append(self.model.final_mask.copy())
        self.model.final_mask = self.model.undo_stack.pop()
        self.model.temp_mask = self.model.final_mask.copy()

    def redo(self) -> None:
        if not self.model.redo_stack:
            return
        self.model.undo_stack.append(self.model.final_mask.copy())
        self.model.final_mask = self.model.redo_stack.pop()
        self.model.temp_mask = self.model.final_mask.copy()