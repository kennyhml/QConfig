from dataclasses import dataclass
from typing import Any, Callable

from PySide6.QtCore import SignalInstance
from PySide6.QtWidgets import QWidget

from ._method_loader import get_method


@dataclass
class Hook:
    """A container for a hook, which provides the ability to invoke calls
    for the mapped widget such as saving or loading a value or adding a
    callback"""

    name: str
    get: Callable[[], Any]
    set: Callable[[Any], None]
    callback: SignalInstance


def build_hook(key: str, widget: QWidget) -> Hook:
    """Builds a hook between a widget and its key in a dataset.

    Parameters
    ----------
    key :class:`key`:
        The key to build the hook for

    widget :class:`QWidget`:
        The widget to hook

    Returns
    -------
    `Hook`:
        A hook for the widget

    Example
    -------
    ```py
    choice_combobox = QComboBox()  # .objectName "choice"
    age_spinbox = QSpinBox()    # .objectName "age"

    data = {"choice": "Choice #3", "age": 18, ...}

    for k in data.keys():
        self.hooks[k] = build_hook(k, self._get_widget([age_spinbox, choice_combobox], k))

    {
        "choice": Hook(name="choice", load="<lambda>", save="<lambda>", ...),
        "age": Hook(name="age", load="<lambda>", save="<lambda>", ...),
    }
    """
    return Hook(
        key,
        *(
            get_method(widget, a)(widget)  # type: ignore[arg-type]
            for a in ["save", "load", "callback"]
        ),
    )
