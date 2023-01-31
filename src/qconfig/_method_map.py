from typing import Any, Callable, Literal, Type

from PySide6.QtWidgets import (QCheckBox, QComboBox, QDoubleSpinBox,
                               QFontComboBox, QLineEdit, QPlainTextEdit,
                               QProgressBar, QPushButton, QSlider, QSpinBox,
                               QStackedWidget, QTabWidget, QTextBrowser,
                               QTextEdit, QWidget)

from .exceptions import UnknownWidgetError

OBJECT_METHOD_MAP: dict[tuple[Type[QWidget], ...], dict[str, Callable[[Any], Any]]] = {
    (QComboBox, QFontComboBox): {
        "save": lambda w: w.currentText,
        "load": lambda w: w.setCurrentText,
        "callback": lambda w: w.currentIndexChanged.connect,
    },
    (QCheckBox, QPushButton): {
        "save": lambda w: w.isChecked,
        "load": lambda w: w.setChecked,
        "callback": lambda w: w.stateChanged.connect,
    },
    (QSpinBox, QDoubleSpinBox, QSlider, QProgressBar): {
        "save": lambda w: w.value,
        "load": lambda w: w.setValue,
        "callback": lambda w: w.valueChanged.connect,
    },
    (QTextEdit, QPlainTextEdit, QTextBrowser, QLineEdit): {
        "save": lambda w: w.toPlainText,
        "load": lambda w: w.setText,
        "callback": lambda w: w.textChanged.connect,
    },
    (QTabWidget, QStackedWidget): {
        "save": lambda w: w.currentIndex,
        "load": lambda w: w.setCurrentIndex,
        "callback": lambda w: w.currentChanged.connect,
    },
}


def get_method(
    widget: QWidget, action: Literal["save", "load", "callback"]
) -> Callable:
    """Gets the method for a widget to execute the given action.

    Parameters
    ----------
    widget :class:`QWidtget`:
        The widget to find the methods of

    action :class:`Literal['save', 'load', 'callback']`:
        The action to get the method for

    Returns
    -------
    `Callable`
        The method for the widget that matches the desired action

    Raises
    ------
    `ValueError`
        When the widget is not of type `QWidget`, or the action is invalid

    `UnknownWidgetError`
        When the widget could not be found, note that this does not mean it's
        not an existing widget, but rather that it is unsupported
    """
    if not isinstance(widget, QWidget):
        raise ValueError(
            f"Invalid widget type. Expected QWidget, got {type(widget).__name__}"
        )

    if action not in ["save", "load", "callback"]:
        raise ValueError(widget, action)

    for k, v in OBJECT_METHOD_MAP.items():
        if type(widget) in k:
            return v[action]

    raise UnknownWidgetError(widget)
