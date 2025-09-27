# base_controller.py
from modules.controller.constants import MaskMode
from modules.controller.file_handler import FileHandler
from modules.controller.gui_config import MaskSelectorGUIConfig, BaseGUIConfig, ThresholdGUIConfig
from modules.controller.gui_config import ParameterAdjusterGUIConfig
from modules.interfaces.interfaces import DisplayInterface, KeyHandlerInterface, MouseHandlerInterface, \
    FileHandlerInterface, RedoUndoInterface
from modules.model.base_model import BaseModel

from modules.controller.mask_manipulator import MaskManipulator
from modules.controller.event_handlers import MouseHandler, KeyboardHandler
from modules.utils import remove_watermark
from modules.view.tkinter_view import TkinterView
from modules.view.pyqt_view import PyQt5View


class BaseController:
    def __init__(self, args):
        self.view: DisplayInterface = PyQt5View(self) if args.gui_type == 'pyqt5' else TkinterView(self)
        self.model = BaseModel(args.pdf_path, args.dpi, args.max_width, args.max_height)

        # Initialize components
        self.file_handler: FileHandlerInterface = FileHandler(self.model)
        self.mask_manipulator = MaskManipulator(self.model)
        self.mouse_handler: MouseHandlerInterface = MouseHandler(self.model, self.mask_manipulator)
        self.keyboard_handler: KeyHandlerInterface = KeyboardHandler(self.model, self.mask_manipulator)

    def update_view(self):
        image = self.model.get_image_to_show()
        if self.model.config_model.get_mode() == MaskMode.ADJUST:
            self.view.update_trackbars(self.model.parameter_model.get_current_parameters())
        self.view.display_image(image)

    def on_weight_trackbar(self, pos):
        self.model.config_model.set_weight(int(pos) / 100.0)
        self.update_view()

    def on_key(self, event):
        if not self.keyboard_handler.handle_key(event):
            if self.model.config_model.get_mode() == MaskMode.THRESHOLD:
                self.mask_manipulator.add_temp_mask_to_final_mask()
                self.change_mode(MaskMode.SELECT)
            else:
                self.next_mode()
        self.update_view()

    def on_click_back(self):
        self.change_mode(MaskMode.SELECT)

    def on_click_prev(self):
        self.model.image_model.prev_image()
        self.update_view()

    def on_click_next(self):
        self.model.image_model.next_image()
        self.update_view()

    def on_click_remove(self):
        self.remove_watermark()
        self.change_mode(MaskMode.SELECT)

    def on_click_select(self):
        self.change_mode(MaskMode.SELECT)

    def on_click_draw(self):
        if self.model.config_model.get_mode() == MaskMode.DRAW:
            self.model.mask_model.toggle_cursor_type()
        else:
            self.change_mode(MaskMode.DRAW)

    def show_dft_filtered_image(self):
        image = self.model.get_experimental_image()
        self.view.display_image(image)

    def on_median_image_number_trackbar(self, pos):
        self.model.image_model.set_median_trackbar_pos(pos)
        self.update_view()

    def on_click_continue(self):
        self.next_mode()

    def on_click_threshold_finished(self):
        self.mask_manipulator.add_temp_mask_to_final_mask()
        self.change_mode(MaskMode.SELECT)

    def on_click_finished_mask(self):
        self.change_mode(MaskMode.ADJUST)

    def next_mode(self):
        if self.model.config_model.get_mode() == MaskMode.DRAW:
            self.change_mode(MaskMode.THRESHOLD)
        elif self.model.config_model.get_mode() == MaskMode.SELECT:
            self.change_mode(MaskMode.THRESHOLD)
        elif self.model.config_model.get_mode() == MaskMode.THRESHOLD:
            self.change_mode(MaskMode.SELECT)
        elif self.model.config_model.get_mode() == MaskMode.ADJUST:
            self.remove_watermark()
            self.change_mode(MaskMode.SELECT)

    def change_mode(self, mode: MaskMode):
        self.model.config_model.set_mode(mode)
        self.change_window_setup()
        self.update_view()

    def change_window_setup(self):
        if self.model.config_model.get_mode() == MaskMode.ADJUST:
            self.view.change_window_setup(ParameterAdjusterGUIConfig.get_params(self))
        elif self.model.config_model.get_mode() == MaskMode.THRESHOLD:
            self.view.change_window_setup(ThresholdGUIConfig.get_params(self))
        else:
            self.view.change_window_setup(BaseGUIConfig.get_params(self))

    def handle_mouse(self, event):
        self.mouse_handler.handle_mouse(event)
        self.update_view()

    def on_threshold_trackbar(self, pos, trackbar_name):
        if trackbar_name == "min":
            self.model.config_model.set_threshold_min(pos)
        elif trackbar_name == "max":
            self.model.config_model.set_threshold_max(pos)
        self.mask_manipulator.apply_thresholds()
        self.update_view()

    def on_toggle_apply_same_parameters(self):
        self.model.toggle_apply_same_parameters()

    #####################################################################

    def on_parameter_changed(self, attr, val):
        self.update_parameter(attr, val)

    def update_parameter(self, attr, val):
        val = int(val)
        setattr(self.model.parameter_model.current_parameters, attr, val)
        if self.model.config_model.config_data.apply_same_parameters:
            for param in self.model.parameter_model.parameters:
                setattr(param, attr, val)
        self.view.display_image(self.model.get_processed_current_image())

    def get_parameters(self):
        return self.model.parameter_model.get_parameters()

    #########################################################################

    def run(self):
        self.view.set_texts(MaskSelectorGUIConfig.TEXTS, MaskSelectorGUIConfig.TEXT_COLOR,
                            MaskSelectorGUIConfig.WINDOW_TITLE)
        self.view.change_window_setup(MaskSelectorGUIConfig.get_params(self))
        self.update_view()
        self.view.start_main_loop()

    # Delegating methods to appropriate components
    def erode_mask(self):
        self.mask_manipulator.erode_mask()
        self.model.save_state()
        self.update_view()

    def dilate_mask(self):
        self.mask_manipulator.dilate_mask()
        self.model.save_state()
        self.update_view()

    def get_threshold_min(self):
        return self.model.config_model.get_threshold_min()

    def get_threshold_max(self):
        return self.model.config_model.get_threshold_max()

    def reset_mask(self):
        self.mask_manipulator.reset_mask()
        self.model.image_model.update_current_image()
        self.update_view()

    def save_mask(self):
        self.file_handler.save_mask()

    def save_images(self):
        self.file_handler.save_images()

    def load_mask(self):
        self.file_handler.load_mask()
        self.update_view()

    def load_images(self):
        self.file_handler.load_images()
        self.change_mode(MaskMode.SELECT)
        self.update_view()

    def redo(self):
        self.model.redo()
        self.update_view()

    def undo(self):
        self.model.undo()
        self.update_view()

    def remove_watermark(self):
        processed_images = remove_watermark(self.model.image_model.get_original_sized_images(),
                                            self.model.get_bgr_mask(),
                                            self.model.parameter_model.get_parameters())
        self.model.update_data(processed_images)


    def exit(self):
        self.view.close_window()
