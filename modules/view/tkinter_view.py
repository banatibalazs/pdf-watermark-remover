# modules/view/tkinter_view.py
import tkinter as tk
from PIL import Image, ImageTk
from modules.utils import add_texts_to_image
from modules.interfaces.gui_interfaces import DisplayInterface

class TkinterView(DisplayInterface):
    def __init__(self, texts, text_color, title):
        self.texts = texts
        self.text_color = text_color
        self.text_pos = (10, 40)
        self.is_text_shown = True
        self.title = title
        self.root = None
        self.label = None

    def setup_window(self, params=None):
        self.root = tk.Tk()
        self.root.title(self.title)
        # self.label = tk.Label(self.root)
        # self.label.pack()

        # Main layout: image left, sidebar right
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.image_label = tk.Label(main_frame)
        self.image_label.pack(side=tk.LEFT, padx=10, pady=10)

        self.sidebar = tk.Frame(main_frame)
        self.sidebar.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        # Texts in sidebar
        self.text_label = tk.Label(self.sidebar, text='\n'.join(self.texts), justify=tk.LEFT)
        self.text_label.pack(anchor='n', pady=5)

        # Add a buttons in a line
        button_frame = tk.Frame(self.sidebar)
        button_frame.pack(anchor='n', pady=5)

        toggle_text_button = tk.Button(button_frame, text='Toggle Text', command=self.toggle_text)
        toggle_text_button.pack(side=tk.LEFT, padx=5)
        close_button = tk.Button(button_frame, text='Close', command=self.close_window)
        close_button.pack(side=tk.LEFT, padx=5)
        redo_button = tk.Button(button_frame, text='Redo', command=lambda: self.update_trackbars(params))
        redo_button.pack(side=tk.LEFT, padx=5)
        undo_button = tk.Button(button_frame, text='Undo', command=lambda: self.update_trackbars(params))
        undo_button.pack(side=tk.LEFT, padx=5)

        if params and 'key' in params:
            self.root.bind('<Key>', params['key'])
        if params and 'trackbars' in params:
            for name, value in params['trackbars'].items():
                if name == 'mode':
                    scale = tk.Scale(self.sidebar, from_=0, to=1, orient='horizontal', label=name,
                                     command=value['callback'], length=200)
                elif name == 'w':
                    scale = tk.Scale(self.sidebar, from_=0, to=25, orient='horizontal', label=name,
                                     command=value['callback'], length=200)
                else:
                    scale = tk.Scale(self.sidebar, from_=0, to=255, orient='horizontal', label=name,
                                     command=value['callback'], length=200)
                scale.set(value['value'])
                scale.pack()
        if params and 'mouse' in params:
            self.image_label.bind('<Button-1>', params['mouse'])
            # add button release event
            self.image_label.bind('<ButtonRelease-1>', params['mouse'])
            # add mouse motion event
            self.image_label.bind('<Motion>', params['mouse'])
            # add every mouse movement event in one line
            self.image_label.bind('<Button-4>', params['mouse'])
            self.image_label.bind('<Button-5>', params['mouse'])

        if "buttons" in params:
            for name, button in params['buttons'].items():
                btn = tk.Button(self.sidebar, text=name, command=button['callback'])
                btn.pack(anchor='n', pady=5)



    def display_image(self, image):

        img = Image.fromarray(image)
        imgtk = ImageTk.PhotoImage(image=img)
        self.image_label.imgtk = imgtk
        self.image_label.config(image=imgtk)
        self.root.update_idletasks()
        self.root.update()


    def close_window(self):
        if self.root:
            self.root.destroy()
            self.root = None

    def update_trackbars(self, params):
        # for i in range(len(params['names'])):
        #     scale = self.root.nametowidget(f'!scale{i}')
        #     scale.set(int(params['values'][i]))
        pass

    def toggle_text(self):
        self.is_text_shown = not self.is_text_shown