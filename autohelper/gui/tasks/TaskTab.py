from typing import List

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QHBoxLayout

from autohelper.gui.Communicate import communicate
from autohelper.gui.tasks.ConfigItemFactory import config_widget_item
from autohelper.gui.tasks.StartButton import StartButton
from autohelper.gui.tasks.TaskOpButton import TaskOpButton
from autohelper.gui.tasks.TooltipTableWidget import TooltipTableWidget
from autohelper.gui.widget.RoundCornerContainer import RoundCornerContainer
from autohelper.logging.Logger import get_logger
from autohelper.task.BaseTask import BaseTask

logger = get_logger(__name__)


class TaskTab(QWidget):
    def __init__(self, tasks: List[BaseTask]):
        super().__init__()

        self.mainLayout = QVBoxLayout(self)
        self.setLayout(self.mainLayout)
        self.tasks = tasks
        # Top row setup with horizontal splitter
        self.top_layout = QHBoxLayout()
        self.task_table = TooltipTableWidget([0.7, 0.15, 0.15])
        self.task_container = RoundCornerContainer("Tasks", self.task_table)
        self.start_button = StartButton()
        self.task_container.add_top_widget(self.start_button)

        self.top_layout.addWidget(self.task_container)
        self.task_labels = ['Name', 'Status', 'Operation']
        self.create_table()
        self.mainLayout.addLayout(self.top_layout)

        self.task_config_table = TooltipTableWidget([0.3, 0.7])
        self.task_config_container = RoundCornerContainer(f"Tasks", self.task_config_table)
        self.task_config_labels = ['Config', 'Value']
        self.task_config_table.setColumnCount(len(self.task_config_labels))  # Name and Value
        self.task_config_table.setHorizontalHeaderLabels(self.task_config_labels)
        self.update_config_table()
        self.mainLayout.addWidget(self.task_config_container)

        communicate.tasks.connect(self.update_table)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_table)
        self.timer.start(1000)

    def update_config_table(self):
        task = self.tasks[self.task_table.selectedIndexes()[0].row()]
        config = task.config
        self.task_config_container.title_label.setText(f"Config: {task.name}")
        self.task_config_table.setRowCount(len(config))
        for row, (key, value) in enumerate(config.items()):
            if not self.task_config_table.item(row, 0):
                item0 = self.uneditable_item()
                self.task_config_table.setItem(row, 0, item0)
            self.task_config_table.item(row, 0).setText(key)
            config_widget_item(self.task_config_table, row, 1, config, key, value)

    def create_table(self):
        self.task_table.setRowCount(len(self.tasks))  # Adjust the row count to match the number of attributes
        self.task_table.setColumnCount(len(self.task_labels))  # Name and Value
        self.task_table.setHorizontalHeaderLabels(self.task_labels)
        self.task_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.task_table.setSelectionMode(QTableWidget.SingleSelection)
        self.task_table.selectRow(0)
        self.task_table.itemSelectionChanged.connect(self.update_config_table)
        for row, task in enumerate(self.tasks):
            for i in range(2):
                item = self.uneditable_item()
                self.task_table.setItem(row, i, item)
            op_button = TaskOpButton(task)
            self.task_table.setCellWidget(row, 2, op_button)
        self.update_table()

    def uneditable_item(self):
        item = QTableWidgetItem()
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
        return item

    def update_table(self):
        for row, task in enumerate(self.tasks):
            self.task_table.item(row, 0).setText(task.name)
            status = task.get_status()
            self.task_table.item(row, 1).setText(status)
            if status == "Running":
                self.task_table.item(row, 1).setBackground(QColor("green"))
            elif status == "Disabled":
                self.task_table.item(row, 1).setBackground(QColor("red"))
            else:
                self.task_table.item(row, 1).setBackground(QColor(0, 0, 0, 0))
            self.task_table.cellWidget(row, 2).update_task(task)
