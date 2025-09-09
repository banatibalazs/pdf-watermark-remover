# modules/interfaces/events.py
from enum import Enum, auto
from dataclasses import dataclass

class EventType(Enum):
    MOUSE_PRESS = auto()
    MOUSE_RELEASE = auto()
    MOUSE_MOVE = auto()
    MOUSE_WHEEL = auto()
    KEY_PRESS = auto()
    KEY_RELEASE = auto()

class MouseButton(Enum):
    LEFT = auto()
    MIDDLE = auto()
    RIGHT = auto()

@dataclass
class AbstractEvent:
    event_type: EventType
    x: int = 0
    y: int = 0

@dataclass
class MouseEvent(AbstractEvent):
    button: MouseButton = None
    wheel_delta: int = 0

@dataclass
class KeyEvent(AbstractEvent):
    key_code: int = 0
    key_char: str = ""