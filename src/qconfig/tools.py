from PySide6.QtWidgets import (QCheckBox, QComboBox, QDateEdit, QDoubleSpinBox,
                               QFontComboBox, QLineEdit, QMainWindow,
                               QPlainTextEdit, QProgressBar, QPushButton,
                               QSlider, QSpinBox, QStackedWidget, QTabWidget,
                               QTextBrowser, QTextEdit, QWidget)

_SUPPORTED_WIDGETS = [
    QComboBox,
    QFontComboBox,
    QCheckBox,
    QSpinBox,
    QDoubleSpinBox,
    QSlider,
    QProgressBar,
    QTextEdit,
    QPlainTextEdit,
    QTextBrowser,
    QLineEdit,
    QTabWidget,
    QStackedWidget,
    QDateEdit
]

def get_all_widgets(parent: QMainWindow) -> list[QWidget]:
    """Gets all children widgets of a parent.
    
    Parameters
    ----------
    parent :class:`QMainWindow`:
        The widget to get the children of
        
    Returns
    -------
    `list[QWidget]`:
        A list of supported children of the parent
    """
    ret = []
    for widget in _SUPPORTED_WIDGETS:
        ret += parent.findChildren(widget)
    return ret
