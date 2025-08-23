# base_controller.py
import numpy as np

from modules.controller.constants import MaskMode
from modules.controller.gui_config import MaskSelectorGUIConfig, BaseGUIConfig
from modules.controller.gui_config import ParameterAdjusterGUIConfig
from modules.model.base_model import BaseModel

from modules.controller.state_manager import MaskStateManager
from modules.controller.mask_manipulator import MaskManipulator
from modules.controller.event_handlers import MouseHandler, KeyboardHandler
from modules.controller.view_updater import ViewUpdater
from modules.watermark_remover import WatermarkRemover


class BaseController:
    def __init__(self, images, view):
        self.view = view
        self.width, self.height = images[0].shape[:2]
        self.model = BaseModel(np.zeros((self.width, self.height), np.uint8), images)

        # Initialize components
        self.view_updater = ViewUpdater(self.model, self.view)
        self.state_manager = MaskStateManager(self.model)
        self.mask_manipulator = MaskManipulator(self.model)
        self.mouse_handler = MouseHandler(self.model, self.state_manager, self.mask_manipulator, self.view_updater)
        self.keyboard_handler = KeyboardHandler(self.model, self.state_manager, self.mask_manipulator,
                                                self.view_updater, self.view)
        self.remover = WatermarkRemover(images, self.model.get_bgr_mask(), self.model.get_parameters())


    def on_weight_trackbar(self, pos):
        self.model.weight = int(pos) / 100.0
        self.view_updater.update_view()

    def on_key(self, event):
        self.keyboard_handler.handle_key(event)

    def on_button_click(self, button_name):
        if button_name == 'select':
            self.change_mode(MaskMode.SELECT)
        elif button_name == 'draw':
            self.change_mode(MaskMode.DRAW)
        elif button_name == 'adjust':
            self.change_mode(MaskMode.ADJUST)
        elif button_name == 'remove':
            self.remove_watermark()
            self.change_mode(MaskMode.SELECT)

    def change_mode(self, mode: MaskMode):
        self.model.set_mode(mode)
        self.change_window_setup()
        self.view_updater.update_view()


    def change_window_setup(self):
        if self.model.mode == MaskMode.ADJUST:
            self.view.change_window_setup(ParameterAdjusterGUIConfig.get_params(self))
        else:
            self.view.change_window_setup(BaseGUIConfig.get_params(self))

    def handle_mouse(self, event):
        self.mouse_handler.handle_mouse(event)

    def on_threshold_trackbar(self, pos, trackbar_name):
        if trackbar_name == "min":
            self.model.threshold_min = pos
        elif trackbar_name == "max":
            self.model.threshold_max = pos
        self.mask_manipulator.apply_thresholds()
        self.view_updater.update_view()

    #####################################################################x

    def on_parameter_changed(self, attr, val):
        self.update_parameter(attr, val)

    def update_parameter(self, attr, val):
        val = int(val)
        setattr(self.model.current_parameters, attr, val)
        if self.model.apply_same_parameters:
            for param in self.model.parameters:
                setattr(param, attr, val)
        self.view.display_image(self.model.get_processed_current_image())

    def get_parameters(self):
        return self.model.get_parameters()

    #########################################################################

    def run(self):
        self.view.setup_window()
        self.view.set_texts(MaskSelectorGUIConfig.TEXTS, MaskSelectorGUIConfig.TEXT_COLOR,
                            MaskSelectorGUIConfig.WINDOW_TITLE)
        self.view.change_window_setup(MaskSelectorGUIConfig.get_params(self))
        self.view_updater.update_view()
        self.view.root.mainloop()

    # Delegating methods to appropriate components
    def erode_mask(self):
        self.mask_manipulator.erode_mask()
        self.state_manager.save_state()
        self.view_updater.update_view()

    def dilate_mask(self):
        self.mask_manipulator.dilate_mask()
        self.state_manager.save_state()
        self.view_updater.update_view()

    def get_gray_mask(self):
        return self.mask_manipulator.get_gray_mask()

    def get_bgr_mask(self):
        return self.mask_manipulator.get_bgr_mask()

    def load_mask(self):
        self.mask_manipulator.load_mask()
        self.view_updater.update_view()

    def reset_mask(self):
        self.mask_manipulator.reset_mask()
        self.model.current_image = self.model.images[self.model.current_page_index].copy()
        self.view_updater.update_view()

    def save_mask(self, path: str = 'saved_mask.png'):
        self.mask_manipulator.save_mask(path)

    def redo(self):
        self.state_manager.redo()
        self.view_updater.update_view()

    def undo(self):
        self.state_manager.undo()
        self.view_updater.update_view()

    def remove_watermark(self):
        self.remover.update_data(self.model.images, self.model.get_bgr_mask(), self.model.get_parameters())
        self.remover.remove_watermark()
        self.model.update_data(self.remover.get_processed_images())


    def exit(self):
        self.view.close_window()
