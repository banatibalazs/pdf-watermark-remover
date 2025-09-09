# modules/controller/event_adapter.py
import tkinter
from modules.interfaces.events import EventType, MouseButton, MouseEvent, KeyEvent


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