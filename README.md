# QConfig
QConfig is a useful tool for PyQt GUI developers, as it makes it easier to save and load the state of the GUI through configuration files. This tool simplifies the process of preserving the current state of the GUI, and provides a range of helpful methods for managing configuration, making it a convenient and efficient solution.

## How to install
QConfig is available on pypi and can be installed via pip.
```py
pip install qtconfig
```

## Introduction
The concept behind the package is a `QConfig` container that takes responsibility for a dictionary of data. Each key in the dictionary gets a `Hook` assigned, which maps the value to its widget.

For datasets with keys that do not match the widget names, a `QConfigDynamicLoader` can be created, mapping each value to its widget, and then passed to the `QConfig` constructor. It is also able to receive a list of keys instead and look for the closest matching widget name.

## Features
- Load all the values a `QConfig` is responsible for from their hooked widgets
- Populate all the widgets with the values a `QConfig`s' data holds
- Add callbacks to the widgets a `QConfig` holds
- Remove specific / all callbacks a `QConfig` holds
- Trigger a "save on change" for all widgets a `QConfig` holds
- Dynamically map config keys to non matching widget object names
- Suppress expected errors while trying to build `QConfigDynamicLoader` or `QConfig`
- Load or read datasets recursively to allow for nested configs
- Convert `str` from config into `QDate` objects

## Why should you use it?
Preserving the state of a GUI in files such as json, yaml or xml yourself can be tedious and results in a lot of boilerplate code. Each widget needs to be connected to the data that holds its value and vice versa, you need to add callbacks to all widgets to invoke a save (unless you want to use a save button or timer) and it takes alot of time, increases the amount of code and increases the risk of getting something wrong. QConfig uses a more sophisticated method of handling the configs for you and allows you to focus on your GUI design rather than worrying about preserving its state.

# Usage
QConfig is very lightweight and intuitive to use, more-so when the configs keys already match the widget names.
## With matching key - widget pairs
The most straightforward way to use QConfig is to ensure that your configuration keys match the widget names in your GUI. Assuming we have the following structure:
```py
user_data: dict[str, Any] = {"user_name": "Jake", "age": 18, "of_age": True, "IQ": 10}
widgets: list[QWidget] = [user_name_widget, age_widget, of_age_checkbox, iq_spinbox]
```

Assuming that each `widget.objectName()` matches the key it is hooked to in the configs, you can create a QConfig just like this:
```py
user_data_qconfig = QConfig(user_data, widgets, recursive=False)
```
## With QConfigDynamicLoader
The QConfigDynamicLoader allows you to dynamically hook a dataset to the widgets even if the keys dont match, by guiding the loader to the widget to search for.
Taking the above example:
```py
user_data: dict[str, any] = {"user_name": "Jake", "age": 18, "of_age": True, "IQ": 10}
widgets: list[QWidget] = [user_name_widget, age_widget, of_age_checkbox, iq_spinbox]
```
Assuming the `objectName()` properties of `user_name_widget` and `age_widget` were actually `"user"` and `"age"` instead, we could create a QConfigDynamicLoader to account for this:
```py
loader = QConfigDynamicLoader({"user_name": "user", "age_widget": "age"}, show_build=True)
user_data_qconfig = QConfig(user_data, widgets, loader, recursive=False)
```
A `QConfigDynamicLoader` is also able to automatically complement keys by close matches, either keys missing in the data or passed as a list. If part of your keys already match with the widget names, they do not need to be added to the loader, the QConfig will find them before accessing the loader.

## Features

Upon initialisation, it will build hooks that connect each key to its respective widget. Now we can use the qconfig object to...

...populate the hooked widgets with the values in the data
```py
user_data_qconfig.load_data()
```
...save the values in the widgets in its key in the data
```py
user_data_qconfig.get_data()
```
...connect callback methods to each widget's change event. With this method when a value in a widget is changed, all the settings will be written to the data right upon change
```py
user_data_qconfig.connect_callback(user_data_qconfig.save_data)
```
...disconnect the callbacks, remove a specified callback by passing one, otherwise all callbacks are disconnected
```py
user_data_qconfig.disconnect_callback(exclude=["user_name"])
```
