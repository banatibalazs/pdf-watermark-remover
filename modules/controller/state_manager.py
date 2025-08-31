# state_manager.py
from modules.model.base_model import BaseModel


class MaskStateManager:
    def __init__(self, model):
        self.model: BaseModel = model

    def save_state(self) -> None:
        self.model.mask_data.temp_mask = self.model.mask_data.final_mask
        self.model.mask_data.undo_stack.append(self.model.mask_data.final_mask.copy())
        self.model.mask_data.redo_stack.clear()

    def undo(self) -> None:
        if not self.model.mask_data.undo_stack:
            return
        self.model.mask_data.redo_stack.append(self.model.mask_data.final_mask.copy())
        self.model.mask_data.final_mask = self.model.mask_data.undo_stack.pop()
        self.model.mask_data.temp_mask = self.model.mask_data.final_mask.copy()

    def redo(self) -> None:
        if not self.model.mask_data.redo_stack:
            return
        self.model.mask_data.undo_stack.append(self.model.mask_data.final_mask.copy())
        self.model.mask_data.final_mask = self.model.mask_data.redo_stack.pop()
        self.model.mask_data.temp_mask = self.model.mask_data.final_mask.copy()

