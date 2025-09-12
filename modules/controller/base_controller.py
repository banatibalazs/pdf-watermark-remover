# base_controller.py
from tkinter import filedialog


from modules.controller.constants import MaskMode
from modules.controller.gui_config import MaskSelectorGUIConfig, BaseGUIConfig
from modules.controller.gui_config import ParameterAdjusterGUIConfig
from modules.interfaces.gui_interfaces import DisplayInterface, KeyHandlerInterface, MouseHandlerInterface
from modules.model.base_model import BaseModel

from modules.controller.state_manager import MaskStateManager
from modules.controller.mask_manipulator import MaskManipulator
from modules.controller.event_handlers import MouseHandler, KeyboardHandler
from modules.utils import remove_watermark, load_pdf, save_images


class BaseController:
    def __init__(self, view: DisplayInterface, args):
        self.view: DisplayInterface = view
        self.model = BaseModel(load_pdf(args.pdf_path, args.dpi), args.dpi, args.max_width, args.max_height)

        # Initialize components
        self.state_manager = MaskStateManager(self.model)
        self.mask_manipulator = MaskManipulator(self.model)
        self.mouse_handler: MouseHandlerInterface = MouseHandler(self.model, self.state_manager, self.mask_manipulator)
        self.keyboard_handler: KeyHandlerInterface = KeyboardHandler(self.model, self.state_manager, self.mask_manipulator)

    def update_view(self):
        image = self.model.get_image_to_show()
        self.view.display_image(image)

    def on_weight_trackbar(self, pos):
        self.model.set_weight(int(pos) / 100.0)
        self.update_view()

    def on_key(self, event):
        if not self.keyboard_handler.handle_key(event):
            self.next_mode()
        self.update_view()

    def on_click_back(self):
        self.change_mode(MaskMode.SELECT)

    def on_click_remove(self):
        self.remove_watermark()
        self.change_mode(MaskMode.SELECT)

    def on_click_select(self):
        self.change_mode(MaskMode.SELECT)

    def on_click_draw(self):
        self.change_mode(MaskMode.DRAW)

    def on_click_continue(self):
        self.change_mode(MaskMode.ADJUST)

    def next_mode(self):
        if self.model.get_mode() == MaskMode.DRAW:
            self.change_mode(MaskMode.ADJUST)
        elif self.model.get_mode() == MaskMode.SELECT:
            self.change_mode(MaskMode.ADJUST)
        elif self.model.get_mode() == MaskMode.ADJUST:
            self.remove_watermark()
            self.change_mode(MaskMode.SELECT)

    def change_mode(self, mode: MaskMode):
        self.model.set_mode(mode)
        print(f"Changed mode to {self.model.get_mode().name}")
        self.change_window_setup()
        self.update_view()


    def change_window_setup(self):
        if self.model.get_mode() == MaskMode.ADJUST:
            self.view.change_window_setup(ParameterAdjusterGUIConfig.get_params(self))
            self.view.set_texts(ParameterAdjusterGUIConfig.TEXTS,
                                ParameterAdjusterGUIConfig.TEXT_COLOR,
                                ParameterAdjusterGUIConfig.TITLE)
        else:
            self.view.change_window_setup(BaseGUIConfig.get_params(self))
            self.view.set_texts(MaskSelectorGUIConfig.TEXTS,
                                MaskSelectorGUIConfig.TEXT_COLOR,
                                MaskSelectorGUIConfig.WINDOW_TITLE)

    def handle_mouse(self, event):
        self.mouse_handler.handle_mouse(event)
        self.update_view()

    def on_threshold_trackbar(self, pos, trackbar_name):
        if trackbar_name == "min":
            self.model.set_threshold_min(pos)
        elif trackbar_name == "max":
            self.model.set_threshold_max(pos)
        self.mask_manipulator.apply_thresholds()
        self.update_view()

    def on_toggle_apply_same_parameters(self):
        self.model.config_data.apply_same_parameters = not self.model.config_data.apply_same_parameters
        print(f"Apply same parameters: {self.model.config_data.apply_same_parameters}")

    #####################################################################x

    def on_parameter_changed(self, attr, val):
        self.update_parameter(attr, val)

    def update_parameter(self, attr, val):
        val = int(val)
        setattr(self.model.current_parameters, attr, val)
        if self.model.config_data.apply_same_parameters:
            for param in self.model.parameters:
                setattr(param, attr, val)
        self.view.display_image(self.model.get_processed_current_image())

    def get_parameters(self):
        return self.model.get_parameters()

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
        self.state_manager.save_state()
        self.update_view()

    def dilate_mask(self):
        self.mask_manipulator.dilate_mask()
        self.state_manager.save_state()
        self.update_view()

    def load_mask(self):
        self.mask_manipulator.load_mask()
        self.update_view()

    def load_images(self):
        path = filedialog.askopenfilename(
            title="Load mask",
            filetypes=[("All files", "*.*")]
        )
        if path:
            images = load_pdf(path, self.model.config_data.dpi)
            self.model.update_data(images)
        self.update_view()

    def get_threshold_min(self):
        return self.model.get_threshold_min()

    def get_threshold_max(self):
        return self.model.get_threshold_max()


    def reset_mask(self):
        self.mask_manipulator.reset_mask()
        self.model.image_data.current_image = self.model.get_current_image().copy()
        self.update_view()

    def save_mask(self):
        self.mask_manipulator.save_mask()

    def save_images(self):
    #     save images from numpy array to the specified path via pymupdf
        save_images(self.model.get_original_sized_images(), 'output')

    def redo(self):
        self.state_manager.redo()
        self.update_view()

    def undo(self):
        self.state_manager.undo()
        self.update_view()

    def remove_watermark(self):
        processed_images = remove_watermark(self.model.get_original_sized_images(),
                                            self.model.get_bgr_mask(),
                                            self.model.get_parameters())
        self.model.update_data(processed_images)


    def exit(self):
        self.view.close_window()
