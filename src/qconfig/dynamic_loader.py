import difflib
import json
from dataclasses import dataclass, field

from PySide6.QtWidgets import QWidget

from .exceptions import InvalidWidgetMappingError


@dataclass
class QConfigDynamicLoader:
    """A helper class to dynamically load configs and map them to their widget
    counterpart, so it can later be used to find the right widget.

    Parameters
    ----------
    data :class:`dict[str, str] | list[str]`:
        The data to build the loader with, either a dictionary mapping each key
        to its corresponding widget directly, or a list of keys to be mapped

    suppress_errors :class:`list[str]`:
        A list of keys to suppress errors for

    complement_keys :class:`bool`:
        Whether to automatically look for the closest match in the widgets to
        assign a widget to each key in the list of keys

    show_build :class:`bool`:
        Whether to print the data in the console after building
    """

    data: dict[str, str] | list[str]
    suppress_errors: list[str] = field(kw_only=True, default_factory=list)
    complement_keys: bool = field(kw_only=True, default=False)
    show_build: bool = field(kw_only=True, default=False)

    def build(self, widgets: list[QWidget]) -> None:
        """Builds the loader with a list of available widgets.

        Parameters
        ----------
        widgets :class:`QWidget`:
            A list of widgets available in the UI

        Raises
        ------
        `ValueError`
            When presented with invalid arguments

        `InvalidWidgetMappingError`
            When the widget to a key could not be found
        """
        widget_names = [w.objectName() for w in widgets]

        if isinstance(self.data, dict):
            self._validate_key_presence(widget_names)
        else:
            self._build_from_list(widget_names)

        if not self.show_build:
            return
        print(f"Building successful!\n{json.dumps(self.built_data, indent=4)}")

    def _validate_key_presence(self, widgets: list[str]) -> None:
        """Helper method to validate that all values in the data are existing
        widgets. When a widget is missing, if the complement flag is `True`
        we try to find the widget and add it."""
        if not isinstance(self.data, dict):
            raise ValueError(f"Invalid data type. Expected dict, got {type(self.data)}")

        for k, v in self.data.items():
            if k in self.suppress_errors or v in widgets:
                continue

            # try to add the missing key
            if self.complement_keys and self._complement(self.data, k, widgets):
                continue

            raise InvalidWidgetMappingError(f"No matching widget for '{v}'")

        self.built_data = self.data

    def _build_from_list(self, widgets: list[str]) -> None:
        """Helper method to build the data from the list of keys,
        when no exact key for a match was found, use difflib to determine
        the closest machtching widget object name for the missing key."""
        if not isinstance(self.data, list):
            raise ValueError(f"Invalid data type. Expected list, got {type(self.data)}")

        matches = {k: k for k in self.data if k in widgets}
        remaining_keys = [k for k in self.data if k not in matches.keys()]
        remaining_widgets = [k for k in widgets if k not in matches.keys()]

        for k in remaining_keys:
            if self.complement_keys and self._complement(matches, k, remaining_widgets):
                continue

            if k in self.suppress_errors:
                continue

            raise InvalidWidgetMappingError(f"No matching widget for '{k}'")
        self.built_data = matches

    @staticmethod
    def _complement(data: dict, key: str, widgets: list[str]) -> bool:
        """Adds a key to a dataset if a close match to the key is found in
        the list of widges. If no match was found it simple does nothing.

        Parameters
        ----------
        data :class:`dict`:
            The dataset to add the key to

        key :class:`str`:
            The key to complement

        widgets :class:`Str`:
            A list of possibly matching widgets

        Returns
        -------
        `bool`
            Whether the key was complemented or not
        """
        matches = difflib.get_close_matches(key, widgets, n=1, cutoff=0.43)
        if matches:
            data[key] = matches[0]
        return bool(matches)
