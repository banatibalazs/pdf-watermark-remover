# state_manager.py
from modules.model.base_model import BaseModel

class State:
    def __init__(self, final_mask, temp_mask):
        self.temp_mask = temp_mask.copy()
        self.final_mask = final_mask.copy()
    def get_state(self):
        return self.final_mask, self.temp_mask


class MaskStateManager:
            def __init__(self, model):
                self.model: BaseModel = model
                self.undo_stack = []
                self.redo_stack = []

            def save_state(self) -> None:
                current_state = State(
                    self.model.mask_data.final_mask,
                    self.model.mask_data.temp_mask
                )
                self.undo_stack.append(current_state)
                self.redo_stack.clear()

            def undo(self) -> None:
                if not self.undo_stack:
                    return

                # Save current state to redo stack
                current_state = State(
                    self.model.mask_data.final_mask,
                    self.model.mask_data.temp_mask
                )
                self.redo_stack.append(current_state)

                # Restore previous state
                previous_state = self.undo_stack.pop()
                self.model.mask_data.final_mask, self.model.mask_data.temp_mask = previous_state.get_state()

            def redo(self) -> None:
                if not self.redo_stack:
                    return

                # Save current state to undo stack
                current_state = State(
                    self.model.mask_data.final_mask,
                    self.model.mask_data.temp_mask
                )
                self.undo_stack.append(current_state)

                # Restore next state
                next_state = self.redo_stack.pop()
                self.model.mask_data.final_mask, self.model.mask_data.temp_mask = next_state.get_state()


