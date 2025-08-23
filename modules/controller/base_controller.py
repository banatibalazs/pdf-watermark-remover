# base_controller.py
import numpy as np

from modules.controller.constants import MaskMode
from modules.controller.gui_config import MaskSelectorGUIConfig
from modules.controller.gui_config import ParameterAdjusterGUIConfig
from modules.model.base_model import BaseModel

from modules.controller.state_manager import MaskStateManager
from modules.controller.mask_manipulator import MaskManipulator
from modules.controller.event_handlers import MouseHandler, KeyboardHandler
from modules.controller.view_updater import ViewUpdater


class BaseController:
    def __init__(self, images, view):
        self.view = view
        self.width, self.height = images[0].shape[:2]
        self.model = BaseModel(np.zeros((self.width, self.height), np.uint8), images)
        self.model.mode = MaskMode.SELECT

        # Initialize components
        self.view_updater = ViewUpdater(self.model, self.view)
        self.state_manager = MaskStateManager(self.model)
        self.mask_manipulator = MaskManipulator(self.model)
        self.mouse_handler = MouseHandler(self.model, self.state_manager, self.mask_manipulator, self.view_updater)
        self.keyboard_handler = KeyboardHandler(self.model, self.state_manager, self.mask_manipulator,
                                                self.view_updater, self.view)

    def on_weight_trackbar(self, pos):
        self.model.weight = int(pos) / 100.0
        self.view_updater.update_view()

    def on_key(self, event):
        key = ord(event.char) if event.char else 255
        if not self.keyboard_handler.handle_key(key):
            # self.view.close_window()
            self.model.mode = MaskMode.ADJUST
            self.view.change_window_setup(ParameterAdjusterGUIConfig.get_params(self))

    def on_button_click(self, button_name):
        if button_name == 'selection':
            self.model.mode = MaskMode.SELECT
        elif button_name == 'drawing':
            self.model.mode = MaskMode.DRAW

    def handle_mouse(self, event):
        if self.model.mode == MaskMode.DRAW:
            self.mouse_handler.handle_draw_mode(event)
        elif self.model.mode == MaskMode.SELECT:
            self.mouse_handler.handle_select_mode(event)


    def on_threshold_trackbar(self, pos, trackbar_name):
        if trackbar_name == "min":
            self.model.threshold_min = pos
        elif trackbar_name == "max":
            self.model.threshold_max = pos
        self.mask_manipulator.apply_thresholds()
        self.view_updater.update_view()

    #####################################################################x
    def update_parameter(self, attr, val):
        val = int(val)
        setattr(self.model.current_parameters, attr, val)
        if self.model.apply_same_parameters:
            for param in self.model.parameters:
                setattr(param, attr, val)
        self.view.display_image(self.model.get_processed_current_image())

    def on_parameter_changed(self, attr, val):
        self.update_parameter(attr, val)

    def on_mode_changed(self, pos):
        print("Mode changed to:", pos)
        self.update_parameter('mode', pos)

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

    def exit(self):
        self.view.close_window()
