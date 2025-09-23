# event_handlers.py
import tkinter
import cv2
import numpy as np
from modules.controller.constants import MaskMode
from modules.controller.mask_manipulator import MaskManipulator
from modules.interfaces.gui_interfaces import KeyHandlerInterface, MouseHandlerInterface
from modules.model.base_model import BaseModel
from modules.interfaces.events import MouseButton, EventType


class MouseHandler(MouseHandlerInterface):
    def __init__(self, model: BaseModel, state_manager, mask_manipulator: MaskManipulator):
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
        x, y = event.x, event.y

        if event.event_type == EventType.MOUSE_PRESS:
            self.state_manager.save_state()
            if event.button == MouseButton.LEFT:
                self.left_button_pressed = True
            elif event.button == MouseButton.RIGHT:
                self.right_button_pressed = True

        elif event.event_type == EventType.MOUSE_RELEASE:
            self.left_button_pressed = False
            self.right_button_pressed = False

        if event.event_type == EventType.MOUSE_MOVE and self.left_button_pressed:
            self.mask_manipulator.draw()
        elif event.event_type == EventType.MOUSE_MOVE and self.right_button_pressed:
            self.mask_manipulator.erase()

        if event.event_type == EventType.MOUSE_WHEEL:
            if event.wheel_delta > 0:
                self.model.cursor_data.size = min(self.model.cursor_data.size + 1, 50)
            else:
                self.model.cursor_data.size = max(self.model.cursor_data.size - 1, 1)

        self.model.cursor_data.pos = (x, y)

    def handle_select_mode(self, event):
        x, y = event.x, event.y

        if event.event_type == EventType.MOUSE_PRESS:
            self.state_manager.save_state()

            if event.button == MouseButton.LEFT:
                self.left_button_pressed = True
                self.model.cursor_data.ix, self.model.cursor_data.iy = x, y
                self.model.mask_data.points.append((x, y))

        elif event.event_type == EventType.MOUSE_MOVE:
            if self.left_button_pressed:
                cv2.line(self.model.image_data.current_image,
                         (self.model.cursor_data.ix, self.model.cursor_data.iy),
                         (x, y), (0, 0, 0), 2)
                self.model.cursor_data.ix, self.model.cursor_data.iy = x, y
                self.model.mask_data.points.append((x, y))

        elif event.event_type == EventType.MOUSE_RELEASE:
            self.left_button_pressed = False
            self.reset_current_image()
            self.model.mask_data.points.append((x, y))
            cv2.fillPoly(self.model.mask_data.temp_mask,
                         [np.array(self.model.mask_data.points)],
                         (255, 255, 255))
            self.model.mask_data.points.clear()

    def reset_current_image(self):
        self.model.update_current_image()


class KeyboardHandler(KeyHandlerInterface):
    def __init__(self, model, state_manager, mask_manipulator):
        self.model: BaseModel = model
        self.state_manager = state_manager
        self.mask_manipulator = mask_manipulator

    def handle_key(self, event) -> bool:
        # the tkinter event has 'char' attribute for character keys, pyqt5 uses 'key_char'
        key = ord(getattr(event, 'char', None) if hasattr(event, 'char') else getattr(event, 'key_char', None))
        if key == ord('a'):
            self.model.prev_image()
        elif key == ord('d'):
            self.model.next_image()
        elif key == ord('r'):
            self.mask_manipulator.reset_mask()
        elif key == ord('u'):
            self.state_manager.undo()
        elif key == ord('y'):
            self.state_manager.redo()
        elif key == ord('c'):
            if self.model.get_mode() != MaskMode.DRAW:
                self.model.set_mode(MaskMode.DRAW)
            self.model.toggle_cursor_type()
        elif key == ord('s'):
            if self.model.get_mode() != MaskMode.SELECT:
                self.model.set_mode(MaskMode.SELECT)
        elif key == ord('e'):
            self.mask_manipulator.erode_mask()
        elif key == ord('q'):
            self.mask_manipulator.dilate_mask()
        elif key == 32:
            return False
        return True
