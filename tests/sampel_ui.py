
import sys

from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QDate, Qt
from .sample_ui_layout import SampleUiLayout


class SampleUi(QMainWindow, SampleUiLayout):

    app = QApplication()

    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)
        self.nationality.addItem("German")
        self.nationality.addItem("French")
        self.nationality.addItem("American")


    def display(self):
        self.show()
        sys.exit(self.app.exec())

