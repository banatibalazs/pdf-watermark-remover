# event_handlers.py
import tkinter
import cv2
import numpy as np
from modules.controller.constants import MaskMode


class MouseHandler:
    def __init__(self, model, state_manager, mask_manipulator, view_updater):
        self.model = model
        self.state_manager = state_manager
        self.mask_manipulator = mask_manipulator
        self.view_updater = view_updater
        self.left_button_pressed = False
        self.right_button_pressed = False

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
            cv2.circle(self.model.final_mask, (x, y), self.model.cursor_size, [255], -1)
        elif type == tkinter.EventType.Motion and self.right_button_pressed:
            cv2.circle(self.model.final_mask, (x, y), self.model.cursor_size, [0], -1)

        if getattr(event, 'num', None) == 4 or getattr(event, 'delta', 0) > 0:
            self.model.cursor_size = min(self.model.cursor_size + 1, 50)
        elif getattr(event, 'num', None) == 5 or getattr(event, 'delta', 0) < 0:
            self.model.cursor_size = max(self.model.cursor_size - 1, 1)

        self.model.cursor_pos = (x, y)
        self.view_updater.update_view()

    def handle_select_mode(self, event):
        type = event.type
        x, y = event.x, event.y

        if type == tkinter.EventType.ButtonPress:
            self.state_manager.save_state()

        if type == tkinter.EventType.ButtonPress and event.num == 1:
            self.left_button_pressed = True
            self.model.ix, self.model.iy = x, y
            self.model.points.append((x, y))
        elif type == tkinter.EventType.Motion:
            if self.left_button_pressed:
                cv2.line(self.model.current_image, (self.model.ix, self.model.iy), (x, y), (0, 0, 0), 2)
                self.model.ix, self.model.iy = x, y
                self.model.points.append((x, y))
        elif type == tkinter.EventType.ButtonRelease:
            self.left_button_pressed = False
            self.reset_current_image()
            self.model.points.append((x, y))
            cv2.fillPoly(self.model.final_mask, [np.array(self.model.points)], (255, 255, 255))
            self.model.points.clear()
            self.mask_manipulator.apply_thresholds()

        self.view_updater.update_view()

    def reset_current_image(self):
        self.model.current_image = self.model.images[self.model.current_page_index].copy()
        self.view_updater.update_view()


class KeyboardHandler:
    def __init__(self, model, state_manager, mask_manipulator, view_updater, view):
        self.model = model
        self.state_manager = state_manager
        self.mask_manipulator = mask_manipulator
        self.view_updater = view_updater
        self.view = view

    def handle_key(self, key):
        if key == ord('a'):
            self.model.current_page_index = max(0, self.model.current_page_index - 1)
            self.reset_current_image()
        elif key == ord('d'):
            self.model.current_page_index = min(len(self.model.images) - 1, self.model.current_page_index + 1)
            self.reset_current_image()
        elif key == ord('r'):
            self.mask_manipulator.reset_mask()
        elif key == ord('c'):
            self.view.toggle_text()
        elif key == ord('u'):
            self.state_manager.undo()
        elif key == ord('y'):
            self.state_manager.redo()
        elif key == 32:
            return False

        self.view_updater.update_view()
        return True

    def reset_current_image(self):
        self.model.current_image = self.model.images[self.model.current_page_index].copy()
        self.view_updater.update_view()