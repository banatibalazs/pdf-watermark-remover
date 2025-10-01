# modules/view/tkinter_view.py
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from modules.utils import add_texts_to_image
from modules.interfaces.interfaces import DisplayInterface
import cv2
from modules.controller.event_adapter import TkinterEventAdapter


class TkinterView(DisplayInterface):
    def __init__(self, texts='', text_color=(0,0,0), title='Tkinter View'):
        self.texts = texts
        self.text_color = text_color
        self.text_pos = (10, 40)
        self.is_text_shown = True
        self.title = title
        self.root = None
        self.label = None
        self.sidebar = None
        self.image_label = None
        self._setup_window()

    def _setup_window(self, params=None):
        self.root = tk.Tk()
        self.root.title(self.title)
        self._create_main_layout()
        self._setup_sidebar_content(params)
        self._bind_events(params)

    def start_main_loop(self):
        self.root.mainloop()

    def change_window_setup(self, params):
        # Clear existing sidebar content
        if self.sidebar:
            for widget in self.sidebar.winfo_children():
                widget.destroy()

        # Recreate sidebar content with new params
        self._setup_sidebar_content(params)

        # Rebind events with new params
        self._bind_events(params)

        # Update window title if provided
        if params and 'title' in params:
            self.root.title(params['title'])

        # Force window update
        self.root.update()

    def _create_main_layout(self):
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.image_label = tk.Label(main_frame)
        self.image_label.pack(side=tk.LEFT, padx=10, pady=10)

        self.sidebar = tk.Frame(main_frame)
        self.sidebar.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

    def _setup_sidebar_content(self, params):
        # Add trackbars
        if params and 'trackbars' in params:
            self._create_trackbars(params['trackbars'])

        # Add buttons
        if params and "buttons" in params:
            self._create_buttons(params['buttons'])

        # Add checkboxes
        if params and "checkboxes" in params:
            self._create_checkboxes(params['checkboxes'])

    def _create_checkboxes(self, checkboxes):
        for name, checkbox in checkboxes.items():
            self.check_var = tk.IntVar(value=1)
            chk = tk.Checkbutton(self.sidebar, text=name, variable=self.check_var, command=checkbox['callback'])
            chk.pack(anchor='w', pady=2)

    def _create_trackbars(self, trackbars):
        for name, value in trackbars.items():
            range_min, range_max = value.get('range', (0, 255))
            scale = tk.Scale(self.sidebar, from_=range_min, to=range_max, orient='horizontal',
                             label=name, command=value['callback'], length=200)
            scale.set(value['value'])
            scale.pack()

    def _create_buttons(self, buttons):
        button_frame = tk.Frame(self.sidebar)
        button_frame.pack(anchor='n', pady=5)

        for name, button in buttons.items():
            row, col = button.get('position', (0, 0))
            colspan = button.get('columnspan', 1)
            margin = button.get('margin', (0, 0, 0, 0))
            bg_color = button.get('bg_color', (200, 200, 200))

            btn = tk.Button(button_frame, text=button['text'], command=button['callback'])
            btn.grid(row=row, column=col, columnspan=colspan,
                padx=(margin[1], margin[3]),  # (left, right)
                pady=(margin[0], margin[2]),  # (top, bottom)
                sticky='ew')

        # Configure columns to expand equally
        for i in range(4):
            button_frame.columnconfigure(i, weight=1)

    def _bind_events(self, params):
        if not params:
            return

        if 'key' in params:
            self.root.bind('<Key>', params['key'])

        if 'mouse' in params:
            def on_mouse_event(evnt):
                abstract_event = TkinterEventAdapter.adapt_event(evnt)
                if abstract_event:
                    params['mouse'](abstract_event)
            mouse_events = [
                '<Button-1>', '<ButtonRelease-1>',
                '<Button-3>', '<ButtonRelease-3>',
                '<Motion>', '<Button-4>', '<Button-5>',
                '<MouseWheel>', '<Button-2>', '<ButtonRelease-2>'
            ]
            for event in mouse_events:
                self.image_label.bind(event, on_mouse_event)

    def display_image(self, image):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(image)
        imgtk = ImageTk.PhotoImage(image=img)
        self.image_label.imgtk = imgtk
        self.image_label.config(image=imgtk)
        self.root.update()

    def set_texts(self, texts, text_color, title):
        self.texts = texts
        self.text_color = text_color
        self.title = title

    def close_window(self):
        if self.root:
            self.root.destroy()
            self.root = None

    def update_trackbars(self, params):
        for widget in self.sidebar.winfo_children():
            if isinstance(widget, tk.Scale) and widget.cget('label') in params['names']:
                index = params['names'].index(widget.cget('label'))
                widget.set(params['values'][index])