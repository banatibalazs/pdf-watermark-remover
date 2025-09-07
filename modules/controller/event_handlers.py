# event_handlers.py
import tkinter
import cv2
import numpy as np
from modules.controller.constants import MaskMode
from modules.interfaces.gui_interfaces import KeyHandlerInterface, MouseHandlerInterface
from modules.model.base_model import BaseModel


class MouseHandler(MouseHandlerInterface):
    def __init__(self, model: BaseModel, state_manager, mask_manipulator):
        self.model: BaseModel = model
        self.state_manager = state_manager
        self.mask_manipulator = mask_manipulator
        self.left_button_pressed = False
        self.right_button_pressed = False

    def handle_mouse(self, event):
        if self.model.get_mode() == MaskMode.DRAW:
            self.handle_draw_mode(event)
        elif self.model.get_mode() == MaskMode.SELECT:
            self.handle_select_mode(event)

    def handle_draw_mode(self, event):
        type = event.type
        x, y = event.x, event.y

        if type == tkinter.EventType.ButtonPress:
            self.state_manager.save_state()
            if event.num == 1:
                self.left_button_pressed = True
            elif event.num == 3:
                self.right_button_pressed = True

        elif type == tkinter.EventType.ButtonRelease:
            self.left_button_pressed = False
            self.right_button_pressed = False
            self.mask_manipulator.apply_thresholds()

        if type == tkinter.EventType.Motion and self.left_button_pressed:
            self.mask_manipulator.draw_white()
        elif type == tkinter.EventType.Motion and self.right_button_pressed:
            self.mask_manipulator.draw_black()

        if getattr(event, 'num', None) == 4 or getattr(event, 'delta', 0) > 0:
            self.model.cursor_data.size = min(self.model.cursor_data.size + 1, 50)
        elif getattr(event, 'num', None) == 5 or getattr(event, 'delta', 0) < 0:
            self.model.cursor_data.size = max(self.model.cursor_data.size - 1, 1)

        self.model.cursor_data.pos = (x, y)


    def handle_select_mode(self, event):
        type = event.type
        x, y = event.x, event.y

        if type == tkinter.EventType.ButtonPress:
            self.state_manager.save_state()
            # self.mask_manipulator.reset_temp_mask()

        if type == tkinter.EventType.ButtonPress and event.num == 1:
            self.left_button_pressed = True
            self.model.cursor_data.ix, self.model.cursor_data.iy = x, y
            self.model.mask_data.points.append((x, y))
        elif type == tkinter.EventType.Motion:
            if self.left_button_pressed:
                cv2.line(self.model.image_data.current_image, (self.model.cursor_data.ix, self.model.cursor_data.iy), (x, y), (0, 0, 0), 2)
                self.model.cursor_data.ix, self.model.cursor_data.iy = x, y
                self.model.mask_data.points.append((x, y))
        elif type == tkinter.EventType.ButtonRelease:
            self.left_button_pressed = False
            self.reset_current_image()
            self.model.mask_data.points.append((x, y))
            cv2.fillPoly(self.model.mask_data.temp_mask, [np.array(self.model.mask_data.points)], (255, 255, 255))
            self.model.mask_data.points.clear()
            self.mask_manipulator.apply_thresholds()

    def reset_current_image(self):
        self.model.image_data.current_image = self.model.image_data.images[self.model.image_data.current_page_index].copy()


class KeyboardHandler(KeyHandlerInterface):
    def __init__(self, model, state_manager, mask_manipulator):
        self.model: BaseModel = model
        self.state_manager = state_manager
        self.mask_manipulator = mask_manipulator

    def handle_key(self, event):
        key = ord(event.char) if event.char else 255
        if key == ord('a'):
            self.model.set_current_page_index(max(0, self.model.get_current_page_index() - 1))
        elif key == ord('d'):
            self.model.set_current_page_index(min(len(self.model.image_data.images) - 1, self.model.get_current_page_index() + 1))
        elif key == ord('r'):
            self.mask_manipulator.reset_mask()
        elif key == ord('u'):
            self.state_manager.undo()
        elif key == ord('y'):
            self.state_manager.redo()
        elif key == ord('c'):
            self.model.toggle_cursor_type()
        elif key == 32:
            return False
        return True
