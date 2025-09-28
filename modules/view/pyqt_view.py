# modules/view/pyqt_view.py
import sys
import cv2
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton,
                             QSlider, QVBoxLayout, QHBoxLayout, QWidget,
                             QFrame, QGridLayout, QCheckBox)
from PyQt5.QtGui import QImage, QPixmap, QIcon
from PyQt5.QtCore import Qt, pyqtSlot
from modules.interfaces.interfaces import DisplayInterface

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


class SidebarBuilder:
    def __init__(self, sidebar, sliders, slider_labels):
        self.sidebar = sidebar
        self.sliders = sliders
        self.slider_labels = slider_labels

    def setup_sidebar_content(self, params):
        # Clear existing content
        if self.sidebar.layout():
            self._clear_layout(self.sidebar.layout())

        # Create new layout
        sidebar_layout = QVBoxLayout(self.sidebar)

        # Trackbars
        if params and 'trackbars' in params:
            self.create_trackbars(params['trackbars'])

        # Checkboxes (if any)
        if params and 'checkboxes' in params:
            self.create_checkboxes(params)

        # Buttons
        if params and 'buttons' in params:
            self.create_buttons(params['buttons'])

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

    def create_checkboxes(self, params):
        if 'checkboxes' in params:
            sidebar_layout = QVBoxLayout()
            for name, value in params['checkboxes'].items():
                checkbox = QCheckBox(name)
                checkbox.setChecked(value.get('value', False))
                checkbox.stateChanged.connect(value['callback'])
                checkbox.setFocusPolicy(Qt.NoFocus)
                sidebar_layout.addWidget(checkbox)
                self.sidebar.layout().addLayout(sidebar_layout)

    def create_trackbars(self, trackbars):
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

    def create_buttons(self, buttons):
        button_grid = QGridLayout()

        for name, button in buttons.items():
            row, col = button.get('position', (0, 0))
            btn = QPushButton(button['text'])
            margin = button.get('margin', (0, 0, 0, 0))
            r, g, b = button.get('bg_color', (75, 75, 75))
            btn.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: rgb({r}, {g}, {b});
                    margin: {margin[0]}px {margin[1]}px {margin[2]}px {margin[3]}px;
                }}
                QPushButton:hover {{
                    background-color: rgb({min(r + 20, 255)}, {min(g + 20, 255)}, {min(b + 20, 255)});
                }}
                """
            )
            btn.clicked.connect(button['callback'])
            btn.setFocusPolicy(Qt.NoFocus)

            if button.get('columnspan', 1) > 1:
                button_grid.addWidget(btn, row, col, 1, button['columnspan'])
            else:
                button_grid.addWidget(btn, row, col)

        self.sidebar.layout().addLayout(button_grid)


class EventBinder:
    def __init__(self, window, image_label):
        self.window = window
        self.image_label = image_label

    def bind_events(self, params):
        if not params:
            return

        if 'key' in params:
            self._bind_key_events(params['key'])

        if 'mouse' in params:
            self._bind_mouse_events(params['mouse'])

    def _bind_key_events(self, key_callback):
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
                    key_callback(abstract_event)
                else:
                    # Call original handler if we couldn't adapt the event
                    original_key_press(event)
            except Exception as e:
                print(f"Error handling key event: {str(e)}")
                # Ensure the application doesn't crash on key handling errors
                original_key_press(event)

        self.window.keyPressEvent = key_handler

    def _bind_mouse_events(self, mouse_callback):
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
                offset_y = max(0, (widget_rect.height() - (image_rect.height() / scale_y)) / 2) if scale_y < 1 else 0

                # Convert to image coordinates with bounds checking
                x = max(0, min(image_rect.width() - 1, int((event.x() - offset_x) * scale_x)))
                y = max(0, min(image_rect.height() - 1, int((event.y() - offset_y) * scale_y)))

                # Create abstract event using adapter
                abstract_event = PyQt5EventAdapter.adapt_mouse_event(event, event_type_str, x, y)

                if abstract_event:
                    # Call the controller's handler with the abstract event
                    mouse_callback(abstract_event)

            except Exception as e:
                print(f"Error in mouse handler: {str(e)}")

        self.image_label.setMouseTracking(True)
        self.image_label.mousePressEvent = lambda e: mouse_handler(e, 'press')
        self.image_label.mouseReleaseEvent = lambda e: mouse_handler(e, 'release')
        self.image_label.mouseMoveEvent = lambda e: mouse_handler(e, 'move')
        self.image_label.wheelEvent = lambda e: mouse_handler(e, 'wheel')



class ImageDisplayManager:
    def display_image(self, image, image_label):
        if image is None:
            return

        # Convert BGR to RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        height, width, channels = image.shape
        bytes_per_line = channels * width

        q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        image_label.setPixmap(pixmap)



class WindowManager:
    def __init__(self, window, app):
        self.window = window
        self.app = app

    def create_main_layout(self, image_label_ref, sidebar_ref):
        central_widget = QWidget()
        self.window.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Image display area
        image_label = QLabel()
        image_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(image_label, 3)
        image_label_ref[0] = image_label  # Store reference

        # Right side container with text area and sidebar
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)

        # Sidebar for controls
        sidebar = QFrame()
        sidebar.setFrameShape(QFrame.StyledPanel)
        sidebar.setMaximumSize(SIDEBAR_MAX_WIDTH, SIDEBAR_MAX_HEIGHT)
        sidebar.setMinimumSize(SIDEBAR_MIN_WIDTH, SIDEBAR_MIN_HEIGHT)
        right_layout.addWidget(sidebar)
        sidebar_ref[0] = sidebar  # Store reference

        right_layout.addStretch()  # Push sidebar to the top
        # Add the right container to main layout
        main_layout.addWidget(right_container, 1)

    def set_dark_theme(self):
        """Apply dark theme to the entire application"""
        self.window.setStyleSheet(DARK_THEME_STYLESHEET)

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


#
class PyQt5View(DisplayInterface):
    def __init__(self, texts='', text_color=(0, 0, 0), title='PDF Watermark Remover'):
        self.texts = texts
        self.text_color = text_color
        self.title = title
        self.is_text_shown = True
        self.app = QApplication.instance() or QApplication(sys.argv)
        self.window = QMainWindow()
        self.window.setWindowTitle(self.title)

        # References to be populated by WindowManager
        self.image_label = None
        self.sidebar = None

        # Collections for UI elements
        self.sliders = {}
        self.slider_labels = {}
        self.text_label = None

        # Initialize managers
        self.window_manager = WindowManager(self.window, self.app)

        # Setup UI components
        self._setup_window()
        self.window_manager.set_dark_theme()
        self.window_manager.set_app_icon()

        # Initialize helpers
        self.sidebar_builder = SidebarBuilder(self.sidebar, self.sliders, self.slider_labels)
        self.event_binder = EventBinder(self.window, self.image_label)
        self.image_manager = ImageDisplayManager()

    def _setup_window(self, params=None):
        # Use lists as ref pointers to get objects back from WindowManager
        image_label_ref = [None]
        sidebar_ref = [None]

        self.window_manager.create_main_layout(image_label_ref, sidebar_ref)
        self.image_label = image_label_ref[0]
        self.sidebar = sidebar_ref[0]

        if params:
            self.change_window_setup(params)

    def change_window_setup(self, params):
        # Update sidebar content and bind events
        self.sidebar_builder.setup_sidebar_content(params)
        self.event_binder.bind_events(params)

        # Update window title if provided
        if params and 'title' in params:
            self.window.setWindowTitle(params['title'])

        self.window.update()

    def display_image(self, image):
        self.image_manager.display_image(image, self.image_label)
        self.window.update()

    def update_trackbars(self, values):
        """Updates trackbar values"""
        if hasattr(self, 'sliders'):
            for i in range(len(values['names'])):
                name = values['names'][i]
                if name in self.sliders:
                    self.sliders[name].setValue(int(values['values'][i]))

            # Process UI events to ensure immediate update
            QApplication.processEvents()

    def set_texts(self, texts, color, title):
        # TODO: Implement this properly
        pass

    def start_main_loop(self):
        self.window.show()
        self.app.exec_()

    def close_window(self):
        if self.window:
            self.window.close()
            self.window = None

    def set_dark_theme(self):
        """Apply dark theme to the entire application"""
        self.window_manager.set_dark_theme()
