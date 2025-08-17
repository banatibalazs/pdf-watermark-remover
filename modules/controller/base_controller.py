from abc import ABC, abstractmethod
import tkinter
from tkinter import filedialog
from typing import Dict, Any, Optional, List, Tuple


class BaseController(ABC):
    def __init__(self):
        self.model = None
        self.view = None


    def undo(self) -> None:
        if not self.model.undo_stack:
            return
        self.model.redo_stack.append(self.model.final_mask.copy())
        self.model.final_mask = self.model.undo_stack.pop()
        self.update_view()

    def redo(self) -> None:
        if not self.model.redo_stack:
            return
        self.model.undo_stack.append(self.model.final_mask.copy())
        self.model.final_mask = self.model.redo_stack.pop()
        self.update_view()

    def save_state(self) -> None:
        self.model.undo_stack.append(self.model.final_mask.copy())
        self.model.redo_stack.clear()


    def get_gray_mask(self) -> Optional[Any]:
        """Get the gray mask from the model"""
        return self.model.get_gray_mask() if self.model else None

    def get_bgr_mask(self) -> Optional[Any]:
        """Get the BGR mask from the model"""
        return self.model.get_bgr_mask() if self.model else None

    def load_mask(self) -> None:
        """Load a mask from the specified path"""
        path = filedialog.askopenfilename(
            title="Load mask",
            filetypes=[("All files", "*.*")]
        )
        if self.model:
            self.model.load_mask(path)
            self.update_view()

    def reset_mask(self) -> None:
        """Reset the mask to its initial state"""
        if self.model:
            self.model.reset_mask()
            self.update_view()

    def save_mask(self, path: str = 'saved_mask.png') -> None:
        """Save the current mask to the specified path"""
        if self.model:
            self.model.save_mask(path)


    def update_view(self):
        self.view.display_image(self.model.get_image_shown())

