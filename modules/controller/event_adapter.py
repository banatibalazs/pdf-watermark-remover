# modules/controller/event_adapter.py
import tkinter
from modules.interfaces.events import EventType, MouseButton, MouseEvent, KeyEvent

from PyQt5.QtCore import Qt
from modules.interfaces.events import EventType, MouseButton, MouseEvent, KeyEvent


class PyQt5EventAdapter:
    @staticmethod
    def adapt_mouse_event(event, event_type_str, x, y):
        """
        Adapt a PyQt5 mouse event to the abstract event system.
        """
        # Map PyQt5 event type string to abstract EventType
        event_type_map = {
            'press': EventType.MOUSE_PRESS,
            'release': EventType.MOUSE_RELEASE,
            'move': EventType.MOUSE_MOVE,
            'wheel': EventType.MOUSE_WHEEL
        }

        # Map PyQt5 mouse buttons to abstract MouseButton
        button_map = {
            Qt.LeftButton: MouseButton.LEFT,
            Qt.MiddleButton: MouseButton.MIDDLE,
            Qt.RightButton: MouseButton.RIGHT,
        }

        event_type = event_type_map.get(event_type_str)
        if not event_type:
            return None

        # Handle wheel events
        if event_type == EventType.MOUSE_WHEEL and hasattr(event, 'angleDelta'):
            wheel_delta = event.angleDelta().y() // 120  # Standard wheel step
            return MouseEvent(event_type, x, y, wheel_delta=wheel_delta)

        # Handle other mouse events
        button = button_map.get(event.button(), None) if hasattr(event, 'button') else None
        return MouseEvent(event_type, x, y, button=button)

    @staticmethod
    def adapt_key_event(event):
        """
        Adapt a PyQt5 key event to the abstract event system.
        """
        if hasattr(event, 'key'):
            key_code = event.key()
            key_char = event.text() if hasattr(event, 'text') else ""
            return KeyEvent(EventType.KEY_PRESS, key_char=key_char, key_code=key_code)
        return None

class TkinterEventAdapter:
    @staticmethod
    def adapt_event(event):
        if hasattr(event, 'type'):
            # Mouse events
            if event.type == tkinter.EventType.ButtonPress:
                button = MouseButton.LEFT if event.num == 1 else MouseButton.RIGHT if event.num == 3 else MouseButton.MIDDLE
                return MouseEvent(EventType.MOUSE_PRESS, event.x, event.y, button)

            elif event.type == tkinter.EventType.ButtonRelease:
                button = MouseButton.LEFT if event.num == 1 else MouseButton.RIGHT if event.num == 3 else MouseButton.MIDDLE
                return MouseEvent(EventType.MOUSE_RELEASE, event.x, event.y, button)

            elif event.type == tkinter.EventType.Motion:
                return MouseEvent(EventType.MOUSE_MOVE, event.x, event.y)

            # Mouse wheel
            elif hasattr(event, 'delta') or event.num in (4, 5):
                delta = event.delta if hasattr(event, 'delta') else (1 if event.num == 4 else -1)
                return MouseEvent(EventType.MOUSE_WHEEL, event.x, event.y, wheel_delta=delta)

        # Key events
        if hasattr(event, 'char') or hasattr(event, 'keysym'):
            key_code = ord(event.char) if event.char else event.keycode if hasattr(event, 'keycode') else 0
            return KeyEvent(EventType.KEY_PRESS, key_char=event.char, key_code=key_code)

        return None