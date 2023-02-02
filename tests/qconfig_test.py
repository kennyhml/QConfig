import unittest

from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QSpinBox,
                               QTextEdit)

from qconfig import QConfig
from qconfig import QConfigDynamicLoader


class QConfigTest(unittest.TestCase):
    data = {
        "age": 19,
        "nationality": "German",
        "employed": False,
        "date_of_birth": "03.01.2004",
    }

    def setUp(self) -> None:
        _ = QApplication()
        self.age_widget = QSpinBox()
        self.age_widget.setObjectName("age")
        self.age_widget.setValue(0)

        self.nationality_widget = QComboBox()
        self.nationality_widget.setObjectName("nationality")
        self.nationality_widget.setCurrentText("French")
        self.nationality_widget.setEditable(True)

        self.employed_widget = QCheckBox()
        self.employed_widget.setObjectName("employed")
        self.employed_widget.setChecked(True)

        self.date_of_birth = QTextEdit()
        self.date_of_birth.setObjectName("date_of_birth")
        self.date_of_birth.setText("18.02.1982")

        self.widgets = [
            self.age_widget,
            self.nationality_widget,
            self.employed_widget,
            self.date_of_birth,
        ]

    def build_without_loader(self) -> None:
        qconfig = QConfig("TestConfig", self.data, self.widgets, recursive=False)
        qconfig.load_data()

        assert self.age_widget.value() == self.data["age"]
        assert self.nationality_widget.currentText() == self.data["nationality"]
        assert self.employed_widget.isChecked() == self.data["employed"]
        assert self.date_of_birth.toPlainText() == self.data["date_of_birth"]

        self.age_widget.setValue(0)
        self.nationality_widget.setCurrentText("French")
        self.employed_widget.setChecked(True)
        self.date_of_birth.setText("18.02.1982")

        qconfig.get_data()

        assert self.age_widget.value() == self.data["age"]
        assert self.nationality_widget.currentText() == self.data["nationality"]
        assert self.employed_widget.isChecked() == self.data["employed"]
        assert self.date_of_birth.toPlainText() == self.data["date_of_birth"]

    def build_with_loader(self) -> None:
        self.employed_widget.setObjectName("has_work")
        self.age_widget.setObjectName("years_old")
        self.date_of_birth.setObjectName("born")

        loader = QConfigDynamicLoader(
            data={
                "age": "years_old",
                "date_of_birth": "born",
                "employed": "has_work",
            }
        )

        qconfig = QConfig("TestConfig", self.data, self.widgets, loader, recursive=False)
        qconfig.load_data()

        assert self.age_widget.value() == self.data["age"]
        assert self.nationality_widget.currentText() == self.data["nationality"]
        assert self.employed_widget.isChecked() == self.data["employed"]
        assert self.date_of_birth.toPlainText() == self.data["date_of_birth"]

        self.age_widget.setValue(0)
        self.nationality_widget.setCurrentText("French")
        self.employed_widget.setChecked(True)
        self.date_of_birth.setText("18.02.1982")

        qconfig.get_data()

        assert self.age_widget.value() == self.data["age"]
        assert self.nationality_widget.currentText() == self.data["nationality"]
        assert self.employed_widget.isChecked() == self.data["employed"]
        assert self.date_of_birth.toPlainText() == self.data["date_of_birth"]

        self.employed_widget.setObjectName("employed")
        self.age_widget.setObjectName("age")
        self.date_of_birth.setObjectName("date_of_birth")


if __name__ == "__main__":
    unittest.main()
