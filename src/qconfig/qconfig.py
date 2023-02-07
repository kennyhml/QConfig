from typing import Any, Callable, Optional

from PySide6.QtWidgets import QWidget

from ._hook import Hook, build_hook
from .dynamic_loader import QConfigDynamicLoader
from .exceptions import WidgetNotFoundError


class QConfig:
    """Simple QConfig data container.
    ---------------------------------
    The QConfig class receives a dictionary of the configuration files which
    it is responsible of keeping in sync with the widgets.
    It is important that the widgets have the same `.objectName()`
    value as their respective key in the dataset.

    Alternatively, you can create and pass a `QConfigDynamicLoader` which
    lets you specify the keymapping in form of a dict, or complement keys
    on its own looking for the closest match.

    Parameters
    ----------
    name :class:`str`:
        The name of the qconfig container

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

    _hooks: dict[str, Hook] = {}

    def __init__(
        self,
        name: str,
        data: dict,
        widgets: list[QWidget],
        loader: Optional[QConfigDynamicLoader] = None,
        *,
        recursive: bool = True,
    ) -> None:
        self.name = name
        self.recursive = recursive
        self._data = data
        self._save_on_change = False

        if loader is None:
            self._build_widget_hooks(data, widgets)
        else:
            self._build_widget_hooks_from_loader(data, widgets, loader)

    def __str__(self) -> str:
        return f"QConfig '{self.name}', responsible for {list(self._data.keys())}"

    def __repr__(self) -> str:
        return f"QConfig(name='{self.name}', data={self._data}, hooks={self._hooks}, recursive={self.recursive})"

    @property
    def hooks(self) -> str:
        return "".join(
            f"{k}: {repr(h.get.__name__)}, {repr(h.set.__name__)}, {repr(h.callback.__class__)}\n"
            for k, h in self._hooks.items()
        )

    @property
    def save_on_change(self) -> bool:
        return self._save_on_change

    @save_on_change.setter
    def save_on_change(self, state: bool) -> None:
        if not state:
            if self._save_on_change:
                self.disconnect_callback(self.get_data)
            self._save_on_change = False
        elif state:
            if not self.save_on_change:
                self.connect_callback(self.get_data)
            self._save_on_change = True

    def load_data(self, data: Optional[dict] = None) -> None:
        """Iterates over all items in the date and finds the corresponding widget,
        then loads the value of the data into the widget

        Parameters
        ----------
        data :class:`dict`:
            The dictionary to read the data from, NOT a copy, if none is
            passed it will load the instance data, allows for recursion

        Raises
        ------
        `LookupError`
            When the widget for a key in the date is missing
        """
        if data is None:
            data = self._data

        for k, v in data.items():
            if isinstance(v, dict):
                self.load_data(v)
                continue

            hook = self._hooks[k]
            hook.set(v)

    def get_data(self, data: Optional[dict] = None) -> None:
        """Iterates over all items in the date and finds the corresponding widget,
        then saves the value of the widget to the data.

        Parameters
        ----------
        data :class:`dict` [Optional]:
            The dictionary to write the data to, NOT a copy, if none is
            passed it will load the instance data, allows for recursion

        Raises
        ------
        `LookupError`
            When the widget for a key in the date is missing
        """
        if data is None:
            data = self._data

        for k, v in data.items():
            if isinstance(v, dict):
                self.get_data(v)
                continue

            hook = self._hooks[k]
            data[k] = hook.get()

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
        for k, hook in self._hooks.items():
            if exclude is not None and k in exclude:
                continue

            hook.callback.connect(lambda: callback())

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
        for k, hook in self._hooks.items():
            if exclude is not None and k in exclude:
                continue
            try:
                hook.callback.disconnect(callback)
            except RuntimeError:
                print(f"Tried disconnecting non connected signal '{callback}'")

    def values_match(self) -> bool:
        return all(hook.get() == self._data[k] for k, hook in self._hooks.items())

    def get_widget_value(self, widget_name: str) -> Any:
        for hook in self._hooks.values():
            if hook.name == widget_name:
                return hook.get()

    def get_data_value(self, key: str) -> Any:
        return self._data[key]

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
            self._hooks[k] = build_hook(k, self._get_widget(widgets, k))

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
            self._hooks[origin_k] = build_hook(k, self._get_widget(widgets, k))

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
