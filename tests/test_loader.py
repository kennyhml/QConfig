import unittest

from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QSpinBox,
                               QTextEdit)

from qconfig import QConfigDynamicLoader


class TestQDynamicLoaderTest(unittest.TestCase):

    def setUp(self) -> None:
        _ = QApplication()
        age_widget = QSpinBox()
        age_widget.setObjectName("age")

        nationality_widget = QComboBox()
        nationality_widget.setObjectName("nationality")

        employed_widget = QCheckBox()
        employed_widget.setObjectName("employed")

        date_of_birth = QTextEdit()
        date_of_birth.setObjectName("date_of_birth")

        self.widgets = [age_widget, nationality_widget, employed_widget, date_of_birth]

    def test_build_from_dict(self) -> None:
        config = {"current_age": "age", "has_job": "employed", "born": "date_of_birth"}
        loader = QConfigDynamicLoader(config)
        loader.build(self.widgets)
        result = loader.built_data
        assert result == config


if __name__ == "__main__":
    unittest.main()
