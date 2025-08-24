# state_manager.py
import numpy as np
from typing import List
import fitz  # PyMuPDF
import cv2
import os


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

    def save_images(self, path: str = 'output') -> None:
        images = [cv2.cvtColor(image, cv2.COLOR_BGR2RGB) for image in self.model.images]
        height, width = images[0].shape[:2]
        doc = fitz.open()
        rect = fitz.Rect(0, 0, width, height)
        for image in images:
            temp_img_path = 'temp_image.png'
            cv2.imwrite(temp_img_path, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
            page = doc.new_page(width=width, height=height)
            page.insert_image(rect, filename=temp_img_path)
        doc.save(f'{path}.pdf')
        doc.close()
        os.remove(temp_img_path)