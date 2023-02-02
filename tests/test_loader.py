import unittest

from qconfig import QConfigDynamicLoader
from qconfig.tools import get_all_widgets

from .sampel_ui import SampleUi


class TestQDynamicLoaderTest(unittest.TestCase):
    def setUp(self) -> None:
        self.ui = SampleUi()
        self.widgets = get_all_widgets(self.ui)

    def test_build_from_dict(self) -> None:
        """Assers that building from a dict is successful"""
        mapping = {
            "name": "user_name",
            "has_job": "employed",
            "born": "date_of_birth",
            "born_in": "place_of_birth",
            "wife": "married",
            "reason": "reason_of_application",
        }

        loader = QConfigDynamicLoader(mapping)
        loader.build(self.widgets)
        result = loader.built_data

        assert result == mapping

    def test_build_from_list(self) -> None:
        """Assers that building from a list with complementing is successful"""
        data = ["name", "date_of", "place_of", "reason"]
        expected = {
            "name": "user_name",
            "date_of": "date_of_birth",
            "place_of": "place_of_birth",
            "reason": "reason_of_application",
        }

        loader = QConfigDynamicLoader(data, complement_keys=True)
        loader.build(self.widgets)
        result = loader.built_data

        assert result == expected

    def test_error_suppression_dict(self) -> None:
        """Assers that suppressing errors when building from a dict
        is successful"""
        mapping = {
            "name": "user_name",
            "xxxxx": "employed",
            "born": "date_of_birth",
            "born_in": "place_of_birth",
            "wife": "married",
            "reason": "reason_of_application",
        }

        loader = QConfigDynamicLoader(mapping, suppress_errors=["xxxxx"])
        loader.build(self.widgets)
        result = loader.built_data

        assert result == mapping

    def test_error_suppression_list(self) -> None:     
        """Assers that suppressing errors when building from a list
        is successful"""
        data = ["name", "xxxxx", "place_of", "reason"]
        expected = {
            "name": "user_name",
            "place_of": "place_of_birth",
            "reason": "reason_of_application",
        }

        loader = QConfigDynamicLoader(data, complement_keys=True, suppress_errors=["xxxxx"])
        loader.build(self.widgets)
        result = loader.built_data

        assert result == expected

if __name__ == "__main__":
    unittest.main()
