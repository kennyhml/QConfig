import unittest

from qconfig import QConfig, QConfigDynamicLoader
from qconfig.tools import get_all_widgets

from .sampel_ui import SampleUi


class TestQConfig(unittest.TestCase):
    data = {
        "user_name": "Kenny",
        "nationality": "German",
        "employed": False,
        "date_of_birth": "03.01.2004",
        "place_of_birth": "Germany",
        "married": False,
        "drivers_license": False,
        "disabled": False,
        "kids": 0,
        "happiness": 10,
        "school_average": 2.3,
        "reason_of_application": "Fun",
    }

    def setUp(self) -> None:
        self.ui = SampleUi()
        self.widgets = get_all_widgets(self.ui)

    def _check_ui_matches_data(self) -> None:
        assert self.ui.user_name.text() == self.data["user_name"]
        assert self.ui.nationality.currentText() == self.data["nationality"]
        assert self.ui.employed.isChecked() == self.data["employed"]
        assert self.ui.date_of_birth.text() == self.data["date_of_birth"]
        assert self.ui.place_of_birth.text() == self.data["place_of_birth"]
        assert self.ui.drivers_license.isChecked() == self.data["drivers_license"]
        assert self.ui.married.isChecked() == self.data["married"]
        assert self.ui.disabled.isChecked() == self.data["disabled"]

        assert self.ui.school_average.value() == self.data["school_average"]
        assert self.ui.happiness.value() == self.data["happiness"]
        assert self.ui.kids.value() == self.data["kids"]
        assert (
            self.ui.reason_of_application.toPlainText()
            == self.data["reason_of_application"]
        )

    def _check_data_matches_ui(self) -> None:
        assert self.data["user_name"] == self.ui.user_name.text()
        assert self.data["nationality"] == self.ui.nationality.currentText()
        assert self.data["employed"] == self.ui.employed.isChecked()
        assert self.data["date_of_birth"] == self.ui.date_of_birth.text()
        assert self.data["place_of_birth"] == self.ui.place_of_birth.text()
        assert self.data["drivers_license"] == self.ui.drivers_license.isChecked()
        assert self.data["married"] == self.ui.married.isChecked()
        assert self.data["disabled"] == self.ui.disabled.isChecked()
        assert self.data["school_average"] == self.ui.school_average.value()
        assert self.data["happiness"] == self.ui.happiness.value()
        assert self.data["kids"] == self.ui.kids.value()
        assert (
            self.data["reason_of_application"]
            == self.ui.reason_of_application.toPlainText()
        )

    def test_build_without_loader(self) -> None:
        qconfig = QConfig("TestConfig", self.data, self.widgets, recursive=False)
        qconfig.load_data()

        self._check_ui_matches_data()

        qconfig.get_data()

        self._check_data_matches_ui()

    def test_build_with_loader(self) -> None:
        self.ui.employed.setObjectName("has_work")
        self.ui.date_of_birth.setObjectName("born_in")
        self.ui.disabled.setObjectName("has_disability")

        loader = QConfigDynamicLoader(
            data={
                "employed": "has_work",
                "date_of_birth": "born_in",
                "disabled": "has_disability",
            }
        )

        qconfig = QConfig(
            "TestConfig", self.data, self.widgets, loader, recursive=False
        )
        qconfig.load_data()

        self._check_ui_matches_data()

        qconfig.get_data()

        self._check_data_matches_ui()

        self.ui.employed.setObjectName("has_work")
        self.ui.date_of_birth.setObjectName("born_in")
        self.ui.disabled.setObjectName("has_disability")

    def test_values_match(self) -> None:
        qconfig = QConfig("TestConfig", self.data, self.widgets, recursive=False)
        qconfig.load_data()

        assert qconfig.values_match()

    def test_values_dont_match(self) -> None:
        qconfig = QConfig("TestConfig", self.data, self.widgets, recursive=False)
        qconfig.load_data()

        self.ui.employed.setChecked(True)

        assert not qconfig.values_match()

        self.ui.employed.setChecked(False)

    def test_value_get(self) -> None:
        qconfig = QConfig("TestConfig", self.data, self.widgets, recursive=False)
        qconfig.load_data()

        self.ui.drivers_license.setChecked(True)

        assert qconfig.get_widget_value("drivers_license") != self.data["drivers_license"]

    def test_widget_value_get(self) -> None:
        qconfig = QConfig("TestConfig", self.data, self.widgets, recursive=False)
        qconfig.load_data()

        self.ui.user_name.setText("Jeffrey") 

        assert qconfig.get_widget_value("user_name") != self.data["user_name"]





if __name__ == "__main__":
    unittest.main()
