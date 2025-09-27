from tkinter import filedialog

from modules.interfaces.interfaces import FileHandlerInterface
from modules.utils import load_pdf, save_images
import os



class FileHandler(FileHandlerInterface):
    def __init__(self, model=None):
        self.model = model

    def load_images(self, path=None, dpi=300):
        path = filedialog.askopenfilename(
            title="Load mask",
            filetypes=[("All files", "*.*")]
        )
        if path:
            images = load_pdf(path, self.model.config_data.dpi)
            self.model.update_data(images)

    def save_images(self):
        """Save processed images to specified path"""
        try:
            output_path = filedialog.asksaveasfile(
                title="Save images",
                filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg;*.jpeg"), ("All files", "*.*")],
                initialfile="output"
            ).name
            if not os.path.exists(output_path):
                os.makedirs(output_path)
            save_images(self.model.get_original_sized_images(), output_path)
            return True
        except Exception as e:
            print(f"Error saving images: {str(e)}")
            return False

    def load_mask(self, path=None):
        """Load mask from file"""
        try:
            path = filedialog.askopenfilename(
                title="Load mask",
                filetypes=[("All files", "*.*")]
            )
            if path:
                self.model.load_mask(path)
        except Exception as e:
            print(f"Error loading mask: {str(e)}")


    def save_mask(self):
        try:
            path = filedialog.asksaveasfile(
                title="Save mask",
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
                initialfile="mask.png"
            ).name
            self.model.save_mask(path)
        except Exception as e:
            print(f"Error saving mask: {str(e)}")
