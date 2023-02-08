from typing import Any

from PySide6.QtWidgets import QWidget


class HookError(Exception):
    """Parent exception for all errors related to hooks"""


class InvalidHookError(HookError):
    """Raised when a key-to-widget map has an invalid pair"""


class HookedWidgetDeletedError(HookError):
    """Raised when the hook on a deleted widget was requested"""

    def __init__(self, hook: object) -> None:
        self.hook = hook

    def __str__(self) -> str:
        return f"Widget deleted for hook '{self.hook}'"


class WidgetAlreadydHookedError(HookError):
    """Raised when attempting to hook a widget that is already hooked,
    unless it was explicitly allowed to hook widgets twice"""

    def __init__(self, widget: object, hooked_in: str) -> None:
        self.widget = widget
        self.hooked_in = hooked_in
    def __str__(self) -> str:
        return f"Widget '{self.widget}' already hooked in '{self.hooked_in}'"


class WidgetError(Exception):
    """Parent exceptions for all errors related to widgets"""


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
        return f"Missing widget for '{self.key}'"


class InvalidWidgetError(ValueError):
    """Raised when a widget is of a wrong type"""

    def __init__(self, widget: QWidget) -> None:
        self.widget = widget

    def __str__(self) -> str:
        return f"Invalid widget: {type(self.widget).__name__}"


class InvalidWidgetArgumentError(ValueError):
    """Raised when the argument to a widget is of a wrong type"""

    def __init__(self, widget: QWidget, argument: Any) -> None:
        self.widget = widget
        self.arg = argument

    def __str__(self) -> str:
        return f"Invalid argument for {self.widget}: {self.arg}"
