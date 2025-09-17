# modules/view/pyqt_view.py
import sys
import cv2
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton,
                             QSlider, QVBoxLayout, QHBoxLayout, QWidget,
                             QFrame, QGridLayout, QCheckBox)
from PyQt5.QtGui import QImage, QPixmap, QIcon
from PyQt5.QtCore import Qt, pyqtSlot
from modules.interfaces.gui_interfaces import DisplayInterface

DARK_THEME_STYLESHEET = """
QWidget {
    background-color: #2D2D30;
    color: #CCCCCC;
}
QLabel {
    color: #CCCCCC;
}
QPushButton {
    background-color: #3E3E42;
    border: 1px solid #555555;
    color: #CCCCCC;
    padding: 5px;
    border-radius: 3px;
}
QPushButton:hover {
    background-color: #4E4E52;
}
QPushButton:pressed {
    background-color: #007ACC;
}
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #1E1E1E;
    color: #CCCCCC;
    border: 1px solid #3E3E42;
}
QCheckBox {
    color: #CCCCCC;
}
QCheckBox::indicator {
    width: 13px;
    height: 13px;
}
QCheckBox::indicator:unchecked {
    border: 1px solid #555555;
    background-color: #2D2D30;
}
QCheckBox::indicator:checked {
    border: 1px solid #007ACC;
    background-color: #007ACC;
}
QScrollBar {
    background-color: #2D2D30;
}
QScrollBar:horizontal {
    height: 15px;
}
QScrollBar:vertical {
    width: 15px;
}
QComboBox {
    background-color: #3E3E42;
    color: #CCCCCC;
    border: 1px solid #555555;
}
QMenu {
    background-color: #1E1E1E;
    color: #CCCCCC;
}
QMenuBar {
    background-color: #2D2D30;
    color: #CCCCCC;
}
"""

SIDEBAR_MAX_WIDTH = 450
SIDEBAR_MIN_WIDTH = 250
SIDEBAR_MAX_HEIGHT = 800
SIDEBAR_MIN_HEIGHT = 500
TEXT_AREA_MIN_HEIGHT = 100
TEXT_AREA_MAX_HEIGHT = 100



def _create_text_area():
    """Create and configure the text area for instructions"""
    text_area = QLabel("Instructions will appear here.")
    text_area.setFrameShape(QFrame.StyledPanel)
    text_area.setAlignment(Qt.AlignTop | Qt.AlignLeft)
    text_area.setWordWrap(True)
    text_area.setMinimumHeight(TEXT_AREA_MIN_HEIGHT)
    text_area.setMaximumHeight(TEXT_AREA_MAX_HEIGHT)
    return text_area


class PyQt5View(DisplayInterface):
    def __init__(self, texts='', text_color=(0, 0, 0), title='PDF Watermark Remover'):
        self.texts = texts
        self.text_color = text_color
        self.title = title
        self.is_text_shown = True
        self.app = QApplication.instance() or QApplication(sys.argv)
        self.window = None
        self.image_label = None
        self.sidebar = None
        self.sliders = {}
        self.slider_labels = {}
        self.text_label = None
        self._setup_window()
        self.set_dark_theme()
        self.set_app_icon()

    def set_app_icon(self, icon_name=None):
        """Set the application icon using a path relative to this script"""
        # Get the directory of the current script file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Navigate to project root (two directories up from modules/view)
        project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
        # Build path to the icon
        icon_path = os.path.join(project_root, 'icons', icon_name or 'filter.png')

        if os.path.exists(icon_path):
            app_icon = QIcon(icon_path)
            self.window.setWindowIcon(app_icon)
            self.app.setWindowIcon(app_icon)
        else:
            print(f"Icon not found at: {icon_path}")

    def _setup_window(self, params=None):
        self.window = QMainWindow()
        self.window.setWindowTitle(self.title)
        self._create_main_layout()
        self._setup_sidebar_content(params)
        self._bind_events(params)

    def _create_main_layout(self):
        central_widget = QWidget()
        self.window.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Image display area
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.image_label, 3)

        # Right side container with text area and sidebar
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)

        # # Text area above sidebar
        # self.text_area = _create_text_area()
        # right_layout.addWidget(self.text_area)# Add the right container to main layout
        # main_layout.addWidget(right_container, 1)

        # Sidebar for controls
        self.sidebar = QFrame()
        self.sidebar.setFrameShape(QFrame.StyledPanel)
        self.sidebar.setMaximumSize(SIDEBAR_MAX_WIDTH, SIDEBAR_MAX_HEIGHT)
        self.sidebar.setMinimumSize(SIDEBAR_MIN_WIDTH, SIDEBAR_MIN_HEIGHT)
        right_layout.addWidget(self.sidebar)

        right_layout.addStretch()  # Push sidebar to the top
        # Add the right container to main layout
        main_layout.addWidget(right_container, 1)


    def _setup_sidebar_content(self, params):
        # Clear existing content
        if self.sidebar.layout():
            def clear_layout(layout):
                while layout.count():
                    item = layout.takeAt(0)
                    widget = item.widget()
                    if widget:
                        widget.deleteLater()
                    elif item.layout():
                        clear_layout(item.layout())

            clear_layout(self.sidebar.layout())

        sidebar_layout = QVBoxLayout(self.sidebar)

        # # Text display
        # self.text_label = QLabel('\n'.join(self.texts))
        # self.text_label.setAlignment(Qt.AlignTop)
        # sidebar_layout.addWidget(self.text_label)

        # Trackbars
        if params and 'trackbars' in params:
            self._create_trackbars(params['trackbars'])

        # Checkboxes (if any)
        if params and 'checkboxes' in params:
            self._create_checkboxes(params)

        # Buttons
        if params and 'buttons' in params:
            self._create_buttons(params['buttons'])

    def _create_checkboxes(self, params):
        if params and 'checkboxes' in params:
            sidebar_layout = QVBoxLayout()
            for name, value in params['checkboxes'].items():
                checkbox = QCheckBox(name)
                checkbox.setChecked(value.get('value', False))
                checkbox.stateChanged.connect(value['callback'])
                checkbox.setFocusPolicy(Qt.NoFocus)
                sidebar_layout.addWidget(checkbox)
                self.sidebar.layout().addLayout(sidebar_layout)

    def _create_trackbars(self, trackbars):
        for name, value in trackbars.items():
            range_min, range_max = value.get('range', (0, 255))
            slider_layout = QVBoxLayout()

            label = QLabel(name)
            slider_layout.addWidget(label)
            self.slider_labels[name] = label  # Store label reference

            slider = QSlider(Qt.Horizontal)
            slider.setMinimum(range_min)
            slider.setMaximum(range_max)
            slider.setValue(int(value['value']))

            # Store reference to the slider
            self.sliders[name] = slider

            # Connect callback
            if isinstance(value['value'], float):
                slider.valueChanged.connect(lambda val, cb=value['callback']: cb(float(val)))
            else:
                slider.valueChanged.connect(lambda val, cb=value['callback']: cb(val))

            slider_layout.addWidget(slider)
            self.sidebar.layout().addLayout(slider_layout)

    def _create_buttons(self, buttons):
        button_grid = QGridLayout()

        for name, button in buttons.items():
            row, col = button.get('position', (0, 0))
            btn = QPushButton(button['text'])
            margin = button.get('margin', (0, 0, 0, 0))
            # include the background color if provided
            r, g, b = button.get('bg_color', (75, 75, 75))
            btn.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: rgb({r}, {g}, {b});
                    margin: {margin[0]}px {margin[1]}px {margin[2]}px {margin[3]}px;
                }}
                QPushButton:hover {{
                    background-color: rgb({min(r+20,255)}, {min(g+20,255)}, {min(b+20,255)});
                }}
                """
            )
            btn.clicked.connect(button['callback'])

            # Apply the focus clearing behavior
            btn.setFocusPolicy(Qt.NoFocus)

            if button.get('columnspan', 1) > 1:
                button_grid.addWidget(btn, row, col, 1, button['columnspan'])
            else:
                button_grid.addWidget(btn, row, col)

        self.sidebar.layout().addLayout(button_grid)

    def _bind_events(self, params):
        if not params:
            return

        if 'key' in params:
            # Store original key press event handler
            original_key_press = self.window.keyPressEvent

            def key_handler(event):
                from modules.controller.event_adapter import PyQt5EventAdapter
                try:
                    # Skip handling for modifier keys like Caps Lock
                    if event.key() in (Qt.Key_CapsLock, Qt.Key_NumLock, Qt.Key_ScrollLock):
                        # Call the original handler for system keys
                        original_key_press(event)
                        return

                    # Handle regular keys
                    abstract_event = PyQt5EventAdapter.adapt_key_event(event)
                    if abstract_event:
                        params['key'](abstract_event)
                    else:
                        # Call original handler if we couldn't adapt the event
                        original_key_press(event)
                except Exception as e:
                    print(f"Error handling key event: {str(e)}")
                    # Ensure the application doesn't crash on key handling errors
                    original_key_press(event)

            self.window.keyPressEvent = key_handler

        if 'mouse' in params:
            from modules.controller.event_adapter import PyQt5EventAdapter

            def mouse_handler(event, event_type_str):
                try:
                    # Check if we have an image displayed
                    if not self.image_label.pixmap() or self.image_label.pixmap().isNull():
                        return

                    # Get dimensions and calculate adjusted coordinates
                    image_rect = self.image_label.pixmap().rect()
                    widget_rect = self.image_label.rect()

                    scale_x = image_rect.width() / max(widget_rect.width(), 1)
                    scale_y = image_rect.height() / max(widget_rect.height(), 1)

                    offset_x = max(0, (widget_rect.width() - (image_rect.width() / scale_x)) / 2) if scale_x < 1 else 0
                    offset_y = max(0,
                                   (widget_rect.height() - (image_rect.height() / scale_y)) / 2) if scale_y < 1 else 0

                    # Convert to image coordinates with bounds checking
                    x = max(0, min(image_rect.width() - 1, int((event.x() - offset_x) * scale_x)))
                    y = max(0, min(image_rect.height() - 1, int((event.y() - offset_y) * scale_y)))

                    # Create abstract event using adapter
                    abstract_event = PyQt5EventAdapter.adapt_mouse_event(event, event_type_str, x, y)

                    if abstract_event:
                        # Call the controller's handler with the abstract event
                        params['mouse'](abstract_event)

                except Exception as e:
                    print(f"Error in mouse handler: {str(e)}")

            self.image_label.setMouseTracking(True)
            self.image_label.mousePressEvent = lambda e: mouse_handler(e, 'press')
            self.image_label.mouseReleaseEvent = lambda e: mouse_handler(e, 'release')
            self.image_label.mouseMoveEvent = lambda e: mouse_handler(e, 'move')
            self.image_label.wheelEvent = lambda e: mouse_handler(e, 'wheel')

    def display_image(self, image):
        if image is None:
            return

        # Convert BGR to RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        height, width, channels = image.shape
        bytes_per_line = channels * width

        q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        self.image_label.setPixmap(pixmap)
        self.window.update()

    def set_texts(self, texts, color, title):
        # # Make sure the text panel exists
        # if not hasattr(self, 'text_area'):
        #     # Create text panel if it doesn't exist
        #     self.text_area = QWidget()
        #     self.text_layout = QVBoxLayout(self.text_area)
        #     self.text_layout.setContentsMargins(10, 10, 10, 10)
        #     self.text_area.setStyleSheet("background-color: #f0f0f0; border-radius: 5px;")
        #
        #     # Add text panel to top of sidebar layout
        #     self.sidebar.layout().insertWidget(0, self.text_area)
        # TODO: Implement this properly
        pass


    def change_window_setup(self, params):
        # Clear existing sidebar content
        self._setup_sidebar_content(params)
        self._bind_events(params)


        if params and 'title' in params:
            self.window.setWindowTitle(params['title'])

        self.window.update()

    def start_main_loop(self):
        self.window.show()
        self.app.exec_()

    def close_window(self):
        if self.window:
            self.window.close()
            self.window = None

    def update_trackbars(self, values):
        """
        Updates trackbar values

        Args:
            values (dict): Dictionary of trackbar names and their new values
            Like this: {'names': ['min', 'max', 'w'],
                        'values': [10, 200, 5]}
        """
        if hasattr(self, 'sliders'):
            for i in range(len(values['names'])):
                name = values['names'][i]
                if name in self.sliders:
                    self.sliders[name].setValue(int(values['values'][i]))

            # Process UI events to ensure immediate update
            QApplication.processEvents()

    def set_dark_theme(self):
        """Apply dark theme to the entire application"""
        self.window.setStyleSheet(DARK_THEME_STYLESHEET)