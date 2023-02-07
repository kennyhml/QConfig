import json
import os
import xml.etree.ElementTree as ET
from typing import Any, Callable, Optional

import yaml  # type: ignore[import]
from PySide6.QtWidgets import QWidget

from ._xml_tools import dict_to_etree, etree_to_dict, write_to_xml_file
from .dynamic_loader import QConfigDynamicLoader
from .qconfig import QConfig


class QConfigFile:
    def __init__(
        self,
        filepath: str,
        widgets: list[QWidget],
        loader: Optional[QConfigDynamicLoader] = None,
        *,
        recursive: bool = False,
    ) -> None:
        self.filepath = filepath
        self.widgets = widgets
        self.loader = loader
        self.recursive = recursive
        self.read()
        self._hook_datasets()
        self.qconfig = self._hook_datasets()

    def read(self) -> None:
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

    def _hook_datasets(self) -> QConfig:
        filename = os.path.basename(self.filepath)
        return QConfig(
            filename, self.data, self.widgets, self.loader, recursive=self.recursive
        )
