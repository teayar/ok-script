from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QHBoxLayout
from qfluentwidgets import FlowLayout, CheckBox

import ok.gui
from ok.gui.tasks.ConfigLabelAndWidget import ConfigLabelAndWidget


class LabelAndMultiSelection(ConfigLabelAndWidget):

    def __init__(self, config_desc, options, config, key: str):
        super().__init__(config_desc, config, key)
        self.key = key
        self.tr_dict = {}
        self.tr_options = []
        self.user_action = True
        for option in options:
            tr = ok.gui.app.tr(option)
            self.tr_options.append(tr)
            self.tr_dict[tr] = option
        self.content_layout = FlowLayout()

        self.add_layout(self.content_layout, stretch=1)
        self.check_boxes = []
        for option in self.tr_options:
            checkbox = CheckBox(option)
            checkbox.checkStateChanged.connect(self.check_changed)
            self.check_boxes.append(checkbox)
            self.content_layout.addWidget(checkbox)
        self.update_value()

    def check_changed(self, checked):
        options = []
        for checkbox in self.check_boxes:
            if checkbox.isChecked():
                option = self.tr_dict.get(checkbox.text())
                options.append(option)
        if self.user_action:
            self.update_config(options)

    def update_value(self):
        self.user_action = False
        for checkbox in self.check_boxes:
            checkbox.setChecked(self.tr_dict[checkbox.text()] in self.config[self.key])
        self.user_action = True


class CheckBoxWidget(QWidget):
    def __init__(self, options):
        super().__init__()

        # Create a horizontal layout
        h_layout = FlowLayout()
        h_layout = QHBoxLayout()

        # Add checkboxes to the layout
        for option in options:  # Example with 5 checkboxes
            checkbox = CheckBox(option)
            h_layout.addWidget(checkbox)


def find_string_index(my_list, target_string):
    try:
        index = my_list.index(target_string)
        return index
    except ValueError:
        return 0
