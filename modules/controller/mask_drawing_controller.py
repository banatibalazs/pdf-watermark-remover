from modules.controller.base_controller import BaseController
from modules.interfaces.gui_interfaces import MouseHandlerInterface, KeyHandlerInterface, DisplayInterface
from modules.model.mask_drawing_model import MaskDrawingModel
import tkinter
import cv2


class MaskDrawing(BaseController):
    TEXTS = ["Draw on the mask.",
             "LMouse/RMouse: erase/draw",
             "Mouse wheel: cursor size",
             "Press 'U'/'Y' to undo/redo.",
             "Press 'R' to reset the mask.",
             "Press 'space' to finish."]
    TEXT_COLOR = (0, 0, 0)
    TITLE = "Mask processing"


    def __init__(self, input_mask, view: DisplayInterface):
        super().__init__()
        self.view = view
        self.view.set_texts(MaskDrawing.TEXTS, MaskDrawing.TEXT_COLOR, MaskDrawing.TITLE)
        self.model = MaskDrawingModel(input_mask)


    def handle_mouse(self, event):
        print("Mouse event:", event.type, "at", event.x, event.y, "with state", event.state)
        print(event)
        type = event.type
        x, y = event.x, event.y

        if type == tkinter.EventType.ButtonPress:
            self.save_state()

        # On left mouse button press, draw a black filled circle
        if event.state == 8464:
            self.model.draw_circle(x, y, erase=True, fill=True)
        #  On right mouse button press, draw a white filled circle
        elif event.state == 9232:
            self.model.draw_circle(x, y, erase=False, fill=True)
        # When scrolling the mouse wheel up increase the cursor size
        elif event.num == 4:
            self.model.adjust_cursor_size(increase=True)
        # When scrolling the mouse wheel down decrease the cursor size
        elif event.num == 5:
            self.model.adjust_cursor_size(increase=False)

        self.model.cursor_pos = (x, y)
        mask = self.model.final_mask.copy()
        cv2.circle(mask, self.model.cursor_pos,
                   self.model.cursor_size, [128],
                   self.model.cursor_thickness)
        self.view.display_image(mask)

    def handle_key(self, key):
        if key == ord('r'):
            self.model.final_mask = self.model.input_mask.copy()
            self.model.undo_stack.clear()
            self.model.redo_stack.clear()
        elif key == ord('c'):
            self.view.toggle_text()
        elif key == ord('u'):
            self.undo()
        elif key == ord('y'):
            self.redo()
        elif key == 32:
            return False
        if key in [ord('r'), ord('c'), ord('u'), ord('y')]:
            self.update_view()
        return True

    def run(self):
        def on_key(event):
            key = ord(event.char) if event.char else 255
            if not self.handle_key(key):
                self.view.close_window()

        params = {
            'mouse': self.handle_mouse,
            'key': on_key,
            'buttons': {
                'save_mask': {
                    'text': 'Save mask', 'callback': self.model.save_mask},
                'reset_mask': {'text': 'Reset mask', 'callback': lambda: self.model.final_mask.copy()},
                'load_mask': {'text': 'Load mask', 'callback': self.load_mask}
            }
        }
        self.view.setup_window(params)
        self.view.display_image(self.model.final_mask)
        self.view.root.mainloop()


