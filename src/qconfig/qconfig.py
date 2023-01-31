from typing import Any, Callable, Literal, Optional

from PySide6.QtCore import SignalInstance
from PySide6.QtWidgets import QWidget

from ._method_loader import get_method
from .dynamic_loader import QConfigDynamicLoader
from .exceptions import WidgetNotFoundError


class QConfig:
    """Simple QConfig data container.
    ------------------------------
    The QConfig class receives a dictionary of the configuration files which
    it is responsible of keeping in sync with the widgets.
    It is important that the widgets have the same `.objectName()`
    value as their respective key in the dataset.

    Alternatively, you can create and pass a `QConfigDynamicLoader` which
    lets you specify the keymapping in form of a dict, or complement keys
    on its own looking for the closest match.

    Parameters
    ----------
    data :class:`dict`:
        The dataset the qconfig class needs to handle

    widgets :class:`list[QWidget]`:
        The list of QWidgets in the ui

    loader :class:`QConfigDynamicLoader` [Optional]:
        A dynamic loader to handle non matching config - widget values

    recursive :class:`bool`:
        Whether to search the dict recursively for sub-dicts to ling
        widgets to

    Example:
    --------
    ```py
    user_data = {"user_name": "Obama", "allow_foo": True, "bar_value": 10}
    user_data_qconfig = QConfig(user_data, recursive=False)

    # Expected widgets with the object names
    ['user_name', 'allow_foo', 'bar_value']

    ```

    With QConfigDynamicLoader:
    -------------------------
    ```py
    user_data = {"user": "Obama", "foo": True, "bar": 10}

    # keys dont match the widget name
    ['user_name', 'allow_foo', 'bar_value']

    loader = QConfigDynamicLoader(
        {"user": "user_name", "foo": "allow_foo", "bar": "bar_value"}
        )self._hooks
    user_data_qconfig = QConfig(user_data, loader, recursive=False)
    ```
    """

    def __init__(
        self,
        data: dict,
        widgets: list[QWidget],
        loader: Optional[QConfigDynamicLoader] = None,
        *,
        recursive: bool = True,
    ) -> None:
        self.recursive = recursive
        self._hooks: dict[str, dict[str, Callable | SignalInstance]] = {}
        self._data = data

        if loader is None:
            self._build_widget_hooks(data, widgets)
        else:
            self._build_widget_hooks_from_loader(data, widgets, loader)

    def sync_data(self, data: Optional[dict] = None) -> None:
        """Iterates over all items in the date and finds the corresponding widget,
        then saves the value of the widget to the data.

        Parameters
        ----------
        data :class:`dict`:
            The dictionary to write the data to, NOT a copy

        Raises
        ------
        `LookupError`
            When the widget for a key in the date is missing
        """
        if data is None:
            data = self._data

        for k, v in data.items():
            if isinstance(v, dict):
                self._sync_values(v)
                continue

            method = self._find_method(k, "save")
            data[k] = method()

    def connect_callback(
        self, callback: Callable, exclude: Optional[list[str]] = None
    ) -> None:
        """Adds a callback to all hooks in the container.

        Parameters
        ----------
        callback :class:`Callback`:
            The callback function, no arguments accepted

        exclude :class:`list[str]`:
            A list of keys not to add the callback to
        """
        for hook, methods in self._hooks.items():
            if exclude is not None and hook in exclude:
                continue

            method = methods["callback"]
            if isinstance(method, SignalInstance):
                method.connect(callback)
            else:
                raise ValueError(f'Expected Signal, got {type(methods["callback"])}')

    def disconnect_callback(
        self, callback: Optional[Callable] = None, exclude: Optional[list[str]] = None
    ) -> None:
        """Removes a callback to all hooks in the container.

        Parameters
        ----------
        callback :class:`Callback` [Optional]:
            The callback function, no arguments accepted, if no callback to
            remove is specified, all callbacks will be disconnected

        exclude :class:`list[str]` [Optional]:
            A list of keys not to add the callback to
        """
        for hook, methods in self._hooks.items():
            if exclude is not None and hook in exclude:
                continue

            method = methods["callback"]
            if isinstance(method, SignalInstance):
                try:
                    method.disconnect(callback)
                except RuntimeError:
                    print(f"Tried disconnecting non connected signal '{callback}'")
            else:
                raise ValueError(f'Expected Signal, got {type(methods["callback"])}')

    def _sync_values(self, data: dict) -> None:
        """Iterates over all items in the date and finds the corresponding widget,
        then saves the value of the widget to the data.

        Parameters
        ----------
        data :class:`dict`:
            The dictionary to write the data to, NOT a copy

        Raises
        ------
        `LookupError`
            When the widget for a key in the date is missing
        """
        for k, v in data.items():
            if isinstance(v, dict):
                self._sync_values(v)
                continue

            method = self._find_method(k, "save")
            data[k] = method()

    def _find_method(self, key: str, action: Literal["save", "load"]) -> Callable:
        """Finds the method to either save or load the state of a key
        in to or from the date.

        Parameters
        ----------
        key :class:`str`:
            The key to find the method of

        action :class:`Literal["save", "load"]`:
            The action to get the method of
        """
        for hook, methods in self._hooks.items():
            if hook != key:
                continue

            method = methods[action]
            if not callable(method):
                raise TypeError(f"Expected callable, got {type(method)}")
            return method
        raise LookupError(f"Failed to find method for {key}")

    def _build_widget_hooks(self, data: dict, widgets: list[QWidget]) -> None:
        """Builds the hooks from each key in the data to the widget.

        Parameters
        ----------
        data :class:`dict`:
            The dictionary containing the values to hook

        widgets :class:`list[QWidget]`:
            A list of possibly matching widgets

        Raises
        ------
        `WidgetNotFoundError`
            When the widget wasnt found
        """
        widget_names = [w.objectName() for w in widgets]
        for k, v in data.items():
            if self.recursive and isinstance(v, dict):
                self._build_widget_hooks(v, widgets)
                continue

            if k not in widget_names:
                return
            self._build_hook(k, self._get_widget(widgets, k))

    def _build_widget_hooks_from_loader(
        self, data: dict, widgets: list[QWidget], loader: QConfigDynamicLoader
    ) -> None:
        """Builds the hooks using a dynamic loader, which means when it cant
        find a matching widget from the config key, it will look in the loader
        build to find the matching widget.

        Parameters
        ----------
        data :class:`dict`:
            The dictionary containing the values to hook

        widgets :class:`list[QWidget]`:
            A list of possibly matching widgets

        loader :class:`QConfigDynamicLoader`:
            The loader to build to hook non matching key-widget pairs

        Raises
        ------
        `WidgetNotFoundError`
            When the widget wasnt found

        Example
        -------
        ```py

        # the widgets
        widgets = ["choice_widget", "age", ...]

        # only the "age" key matches its widget
        data = {"choice": "Choice #3", "age": 18, ...}

        # build the loader to fix the choice key to the right widget
        loader.build_data = {"choice": "choice_widget", ...}
        """
        # build the loader with the widgets
        loader.build(widgets)
        widget_names = [w.objectName() for w in widgets]

        for k, v in data.items():
            if self.recursive and isinstance(v, dict):
                self._build_widget_hooks_from_loader(v, widgets, loader)
                continue

            # check if k matches, else if k is in the dynamic loader,
            # if k is in neither of them then we are missing a widget
            origin_k = k
            if k not in widget_names:
                if k not in loader.built_data.keys():
                    raise WidgetNotFoundError(k)
                k = loader.built_data[k]
            self._build_hook(origin_k, self._get_widget(widgets, k))

    def _build_hook(self, key: str, widget: QWidget) -> None:
        """Builds a hook to a key in the config to its widget calls.

        Parameters
        ----------
        key :class:`key`:
            The key to build the hook for

        widget :class:`QWidget`:
            The widget to hook

        Example
        -------
        ```py
        choice_combobox = QComboBox()  # .objectName "choice"
        age_spinbox = QSpinBox()    # .objectName "age"

        data = {"choice": "Choice #3", "age": 18, ...}

        for k in data.keys():
            self._build_hook(k, self._get_widget([age_spinbox, choice_combobox], k))

        {
            "choice": {"save": lambda w: w.currentText, "load": lambda w: w.setCurrentText, ...},
            "age": {"save": lambda w: w.value, "load": lambda w: w.setValue, ...},
        }
        """
        hook = {
            action: method(widget)
            for action, method in [
                (
                    a,
                    get_method(widget, a),  # type:ignore[arg-type]
                )
                for a in ["save", "load", "callback"]
            ]
        }
        self._hooks[key] = hook

    @staticmethod
    def _get_widget(widgets: list[QWidget], key: str) -> QWidget:
        """Finds a key matching a widgets objectName in a list of widgets.

        Parameters
        ----------
        widgets :class:`list[QWidget]`:
            A list of possible widgets

        key :class:`str`:
            The key to find the widget of

        Returns
        -------
        `QWidget`:
            The widget matching the key

        Raises
        ------
        `WidgetNotFoundError`
            When the widget wasnt found
        """
        for w in widgets:
            if w.objectName() == key:
                return w
        raise WidgetNotFoundError(key)
