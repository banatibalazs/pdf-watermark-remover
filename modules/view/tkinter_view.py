# modules/view/tkinter_view.py
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from modules.utils import add_texts_to_image
from modules.interfaces.gui_interfaces import DisplayInterface
import cv2

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

    def setup_window(self, params=None):
        self.root = tk.Tk()
        self.root.title(self.title)
        self._create_main_layout()
        self._setup_sidebar_content(params)
        self._bind_events(params)

    def change_window_setup(self, params):
        print("Changing window setup with params:", params)
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
        # Text label
        self.text_label = tk.Label(self.sidebar, text='\n'.join(self.texts), justify=tk.LEFT)
        self.text_label.pack(anchor='n', pady=5)

        # Close button
        button_frame = tk.Frame(self.sidebar)
        button_frame.pack(anchor='n', pady=5)
        tk.Button(button_frame, text='Close', command=self.close_window).pack(side=tk.LEFT, padx=5)

        # Trackbars
        if params and 'trackbars' in params:
            self._create_trackbars(params['trackbars'])

        # Additional buttons
        if params and "buttons" in params:
            self._create_buttons(params['buttons'])

    def _create_trackbars(self, trackbars):
        trackbar_configs = {
            'mode': {'range': (0, 1)},
            'w': {'range': (0, 25)},
            'default': {'range': (0, 255)}
        }

        for name, value in trackbars.items():
            config = trackbar_configs.get(name, trackbar_configs['default'])
            scale = tk.Scale(
                self.sidebar,
                from_=config['range'][0],
                to=config['range'][1],
                orient='horizontal',
                label=name,
                command=value['callback'],
                length=200
            )
            scale.set(value['value'])
            scale.pack()


    def _create_buttons(self, buttons):
        for name, button in buttons.items():
            tk.Button(
                self.sidebar,
                text=button['text'],  # Use the text from config
                command=button['callback']  # Lambda already has the button name
            ).pack(anchor='n', pady=5)


    def _bind_events(self, params):
        if not params:
            return

        if 'key' in params:
            self.root.bind('<Key>', params['key'])

        if 'mouse' in params:
            mouse_events = [
                '<Button-1>', '<ButtonRelease-1>',
                '<Button-3>', '<ButtonRelease-3>',
                '<Motion>', '<Button-4>', '<Button-5>',
                '<MouseWheel>', '<Button-2>', '<ButtonRelease-2>'
            ]
            for event in mouse_events:
                self.image_label.bind(event, params['mouse'])

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
        for i in range(len(params['names'])):
            trackbar_name = params['names'][i]
            value = int(params['values'][i])
            scale = self.sidebar.nametowidget(trackbar_name)
            if scale:
                scale.set(value)
