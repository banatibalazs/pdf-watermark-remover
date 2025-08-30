# state_manager.py
import fitz  # PyMuPDF
import cv2
import os

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

    # modules/controller/state_manager.py
    def save_images(self, path: str = 'output') -> None:
        images = [cv2.cvtColor(image, cv2.COLOR_BGR2RGB) for image in self.model.image_data.original_sized_images]
        height, width = images[0].shape[:2]
        doc = fitz.open()
        rect = fitz.Rect(0, 0, width, height)
        for image in images:
            temp_img_path = 'temp_image.jpg'
            # Save as JPEG with quality 90
            cv2.imwrite(temp_img_path, cv2.cvtColor(image, cv2.COLOR_RGB2BGR), [int(cv2.IMWRITE_JPEG_QUALITY), 90])
            page = doc.new_page(width=width, height=height)
            page.insert_image(rect, filename=temp_img_path)
        # Use compression options
        doc.save(f'{path}.pdf', deflate=True, garbage=4)
        doc.close()
        os.remove(temp_img_path)
        print(f"Images saved as {path}.pdf")