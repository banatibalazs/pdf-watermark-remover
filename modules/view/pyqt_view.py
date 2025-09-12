# modules/view/pyqt_view.py
import sys
import cv2
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton,
                             QSlider, QVBoxLayout, QHBoxLayout, QWidget,
                             QFrame, QGridLayout, QCheckBox)
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, pyqtSlot
from modules.interfaces.gui_interfaces import DisplayInterface


def _create_text_area():
    """Create and configure the text area for instructions"""
    text_area = QLabel("Instructions will appear here.")
    text_area.setFrameShape(QFrame.StyledPanel)
    text_area.setAlignment(Qt.AlignTop | Qt.AlignLeft)
    text_area.setWordWrap(True)
    text_area.setMinimumHeight(100)
    text_area.setMaximumHeight(100)
    return text_area


class PyQt5View(DisplayInterface):
    def __init__(self, texts='', text_color=(0, 0, 0), title='PyQt5 View'):
        self.texts = texts
        self.text_color = text_color
        self.title = title
        self.is_text_shown = True
        self.app = QApplication.instance() or QApplication(sys.argv)
        self.window = None
        self.image_label = None
        self.sidebar = None
        self.text_label = None
        self._setup_window()

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

        # Text area above sidebar
        self.text_area = _create_text_area()
        right_layout.addWidget(self.text_area)# Add the right container to main layout
        main_layout.addWidget(right_container, 1)

        # Sidebar for controls
        self.sidebar = QFrame()
        self.sidebar.setFrameShape(QFrame.StyledPanel)
        self.sidebar.setMaximumSize(350, 350)  # Reduced height to accommodate text area
        self.sidebar.setMinimumSize(250, 250)
        right_layout.addWidget(self.sidebar)

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

        # Text display
        self.text_label = QLabel('\n'.join(self.texts))
        self.text_label.setAlignment(Qt.AlignTop)
        sidebar_layout.addWidget(self.text_label)

        # Trackbars
        if params and 'trackbars' in params:
            self._create_trackbars(params['trackbars'])

        # Buttons
        if params and 'buttons' in params:
            self._create_buttons(params['buttons'])

        # Checkboxes (if any)
        if params and 'checkboxes' in params:
            self._create_checkboxes(params)

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

            slider = QSlider(Qt.Horizontal)
            slider.setMinimum(range_min)
            slider.setMaximum(range_max)
            # Convert float to int for slider
            slider.setValue(int(value['value']))

            # Preserve the original value type when calling the callback
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
            btn.clicked.connect(button['callback'])
            # Apply the focus clearing behavior
            btn.setFocusPolicy(Qt.NoFocus)
            button_grid.addWidget(btn, row, col)

        self.sidebar.layout().addLayout(button_grid)

    def _bind_events(self, params):
        if not params:
            return

        if 'key' in params:
            def key_handler(event):
                from modules.controller.event_adapter import PyQt5EventAdapter
                abstract_event = PyQt5EventAdapter.adapt_key_event(event)
                if abstract_event:
                    params['key'](abstract_event)

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
        # Make sure the text panel exists
        if not hasattr(self, 'text_area'):
            # Create text panel if it doesn't exist
            self.text_area = QWidget()
            self.text_layout = QVBoxLayout(self.text_area)
            self.text_layout.setContentsMargins(10, 10, 10, 10)
            self.text_area.setStyleSheet("background-color: #f0f0f0; border-radius: 5px;")

            # Add text panel to top of sidebar layout
            self.sidebar.layout().insertWidget(0, self.text_area)


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

    def update_trackbars(self, params):
        if not self.sidebar or not self.sidebar.layout():
            return

        # Find sliders by their labels and update values
        for i in range(self.sidebar.layout().count()):
            item = self.sidebar.layout().itemAt(i)
            if item and item.layout():
                for j in range(item.layout().count()):
                    widget = item.layout().itemAt(j).widget()
                    if isinstance(widget, QSlider) and widget.objectName() in params['names']:
                        index = params['names'].index(widget.objectName())
                        widget.setValue(params['values'][index])