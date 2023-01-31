from src.qconfig import QConfig, QConfigDynamicLoader


from PySide6.QtWidgets import QWidget, QApplication, QComboBox, QSpinBox, QCheckBox

def hi():
    print("HI")

def bye():
    print("BYE")

if __name__ == "__main__":

    app = QApplication()

    choice = QComboBox()
    choice.setObjectName("choice")

    click = QCheckBox()
    click.setObjectName("click")

    spin = QSpinBox()
    spin.setObjectName("spin")

    spin1 = QSpinBox()
    spin1.setObjectName("foo")

    spin2 = QSpinBox()
    spin2.setObjectName("bar")

    spin3 = QSpinBox()
    spin3.setObjectName("foobar")
    spin3.setValue(55)

    widgets = [choice, click, spin, spin1, spin2, spin3]
    settings = {"choice": "food", "click": "right", "spin": "cicles", "something": {"foo": "doo", "bar": "dar", "foobar": "barfoo"}}
    conf = QConfig(settings, widgets)
    conf.sync_data()
    print(settings)
