from __future__ import annotations

import json
import os
import xml.etree.ElementTree as ET
from typing import Any, Callable, Optional

import yaml  # type:ignore[import]
from PySide6.QtWidgets import QWidget

from ._hook import Hook, build_hook
from ._xml_tools import dict_to_etree, etree_to_dict, write_to_xml_file
from .dynamic_loader import QConfigDynamicLoader
from .exceptions import WidgetAlreadydHookedError, WidgetNotFoundError


class QConfig:
    """QConfig Data Container

    The QConfig class manages the configuration data for a set of QWidgets. It can
    either receive a dictionary of the configuration data, or the path to a file
    storing the data. It is important that the QWidgets in the list have the same
    `.objectName()` value as the respective key in the dataset.

    The QConfig class can also be used with a `QConfigDynamicLoader` to handle
    key mappings and missing keys in the dataset.

    Parameters
    ----------
    name :class:`str`:
        The name of the qconfig container

    widgets :class:`list[QWidget]`:
        The list of QWidgets in the ui

    data :class:`dict` [Optional]:
        The dataset the qconfig class needs to handle

    filepath :class:`str` [Optional]:
        The path to the file storing the contents, allows to write or read

    loader :class:`QConfigDynamicLoader` [Optional]:
        A dynamic loader to handle non matching config - widget values

    recursive :class:`bool`:
        Whether to search the dict recursively for sub-dicts to link widgets to

    Raises
    ------
        `ValueError` when neither `data` nor a `filepath` were passed

    Example:
    --------
    ```py
    # Expected widgets with the object names
    widgets = ['user_name', 'allow_foo', 'bar_value']

    user_data = {"user_name": "Joe", "allow_foo": True, "bar_value": 10}
    user_data_qconfig = QConfig("Userdata", widgets, user_data, recursive=False)
    ```

    With QConfigDynamicLoader:
    ```py
    # keys dont match the widget name
    widgets = ['user_name', 'allow_foo', 'bar_value']
    user_data = {"user": "Obama", "foo": True, "bar": 10}

    loader = QConfigDynamicLoader({"user": "user_name", "foo": "allow_foo", "bar": "bar_value"})
    user_data_qconfig = QConfig("Userdata", widgets, user_data, loader=loader, recursive=False)
    ```
    """

    _hooked_widgets: dict[str, list[str]] = {}

    def __init__(
        self,
        name: str,
        widgets: list[QWidget],
        data: Optional[dict] = None,
        filepath: Optional[str] = None,
        loader: Optional[QConfigDynamicLoader] = None,
        *,
        recursive: bool = True,
        allow_multiple_hooks: bool = False,
    ) -> None:
        self._name = name
        self._recursive = recursive
        self.filepath = filepath
        self.allow_mutliple_hooks = allow_multiple_hooks
        self._save_on_change = False
        self._hooks: dict[str, Hook] = {}

        if data is None and filepath is None:
            raise ValueError("Either `data` or `filepath` must be provided.")

        if data is not None:
            self._data = data
        else:
            self.read()
        if loader is None:
            self._build_widget_hooks(self._data, widgets)
        else:
            self._build_widget_hooks_from_loader(self._data, widgets, loader)

    def __del__(self) -> None:
        if self._name in self._hooked_widgets.keys():
            self._hooked_widgets.pop(self._name)

    def __str__(self) -> str:
        return f"QConfig '{self._name}', responsible for {list(self._data.keys())}"

    def __repr__(self) -> str:
        return "\n".join(
            f"{k}: {h.get.__name__}, {h.set.__name__}, {h.callback.__class__}"
            for k, h in self._hooks.items()
        )

    @property
    def name(self) -> str:
        return self._name

    @property
    def save_on_change(self) -> bool:
        return self._save_on_change

    @save_on_change.setter
    def save_on_change(self, state: bool) -> None:
        if not state:
            if self._save_on_change:
                self.disconnect_callback(self.get_data)
            self._save_on_change = False
        else:
            if not self.save_on_change:
                self.connect_callback(self.get_data)
            self._save_on_change = True

    def read(self) -> None:
        """Reads the data provided as the `filepath`.

        Can replace `data` upon instantiation, or be used to sync with other
        components that may alter the contents of the file independently.

        Raises
        ------
        `ValueError`:
            When no filepath or a filepath with an unknown extension was provided

        `FileNotFoundError`:
            When the file at the filepath does not exist
        """
        if self.filepath is None:
            raise ValueError("Can't read from file because no filepath is provided.")

        _, extension = os.path.splitext(self.filepath)

        if extension == ".json":
            with open(self.filepath, "r") as f:
                self.data = json.load(f)

        elif extension == ".xml":
            tree = ET.parse(self.filepath)
            root = tree.getroot()
            self.data = etree_to_dict(root)

        elif extension in [".yaml", ".yml"]:
            with open(self.filepath, "r") as f:
                self.data = yaml.safe_load(f)
        else:
            raise ValueError(f"Unsupported file format: {extension}")

    def write(self) -> None:
        """Writes the data to the file provided as `filepath`.

        Useful to sync with other components that may alter the contents of the
        file independently.

        Raises
        ------
        `ValueError`:
            When no filepath or a filepath with an unknown extension was provided
        """
        if self.filepath is None:
            raise ValueError("Can't read from file because no filepath is provided.")

        _, extension = os.path.splitext(self.filepath)
        if extension == ".json":
            with open(self.filepath, "w") as f:
                json.dump(self.data, f, indent=4)

        elif extension == ".xml":
            data = dict_to_etree(self.data)
            write_to_xml_file(data, self.filepath)

        elif extension in [".yaml", ".yml"]:
            with open(self.filepath, "w") as f:
                yaml.dump(self.data, f)

    def set_data(self, data: Optional[dict] = None) -> None:
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
                self.set_data(v)
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

    def _check_widget_not_hooked(self, widget_name: str) -> None:
        """Checks whether a widget is already hooked in another QConfig.

        Parameters
        ----------
        widget_name :class:`str`:
            The name of the widget to check whether it is hooked

        Raises
        -------
        `WidgetAlreadydHookedError`
            If the widget is already hooked
        """
        for name, widgets in self._hooked_widgets.items():
            if widget_name in widgets:
                raise WidgetAlreadydHookedError(widget_name, name)

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
        self._hooked_widgets[self._name] = []
        widget_names = [w.objectName() for w in widgets]
        for k, v in data.items():
            if not self.allow_mutliple_hooks:
                self._check_widget_not_hooked(k)

            if self._recursive and isinstance(v, dict):
                self._build_widget_hooks(v, widgets)
                continue

            if k not in widget_names:
                return
            self._hooks[k] = build_hook(k, self._get_widget(widgets, k))
            self._hooked_widgets[self._name].append(k)

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
        self._hooked_widgets[self._name] = []
        widget_names = [w.objectName() for w in widgets]

        for k, v in data.items():
            if not self.allow_mutliple_hooks:
                self._check_widget_not_hooked(k)

            if self._recursive and isinstance(v, dict):
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
            self._hooked_widgets[self._name].append(k)

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
