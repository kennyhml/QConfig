from PySide6.QtWidgets import QWidget


class InvalidWidgetMappingError(LookupError):
    """Raised when a key-to-widget map has an invalid pair"""


class HookedWidgetDeletedError(Exception):
    """Raised when the hook on a deleted widget was requested"""

    def __init__(self, hook: object) -> None:
        self.hook = hook

    def __str__(self) -> str:
        return f"Widget deleted for hook '{self.hook}'"

class UnknownWidgetError(LookupError):
    """Raised when the method for a widget could not be found"""

    def __init__(self, widget: QWidget) -> None:
        self.widget = widget

    def __str__(self) -> str:
        return f"Not yet supported widget: {type(self.widget).__name__}"


class WidgetNotFoundError(LookupError):
    """Raised when a widget could not be found"""

    def __init__(self, key: str) -> None:
        self.key = key

    def __str__(self) -> str:
        return f"Missing widget for {self.key}"


class InvalidWidgetError(ValueError):
    """Raised when a widget is of a wrong type"""

    def __init__(self, widget: QWidget) -> None:
        self.widget = widget

    def __str__(self) -> str:
        return f"Invalid widget: {type(self.widget).__name__}"


class InvalidActionError(ValueError):
    """Raised when a widget is of a wrong type"""

    def __init__(self, widget: QWidget, action: str) -> None:
        self.widget = widget
        self.action = action

    def __str__(self) -> str:
        return f"Invalid action for {self.widget}: {self.action}"
