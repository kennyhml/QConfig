from dataclasses import dataclass
from typing import Any, Callable

from PySide6.QtCore import SignalInstance
from PySide6.QtWidgets import QWidget

from ._method_loader import get_method


@dataclass
class Hook:

    name: str
    save: Callable[[], Any]
    load: Callable[[Any], None]
    callback: SignalInstance


def build_hook(key: str, widget: QWidget) -> Hook:
    """Builds a hook to a key in the config to its widget calls.

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
        self._build_hook(k, self._get_widget([age_spinbox, choice_combobox], k))

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