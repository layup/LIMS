
from PyQt5.QtCore import QDateTime, QTimer
from PyQt5.QtWidgets import  QLabel, QMessageBox


class StatusBarManager:
    def __init__(self, statusbar):
        self.statusbar = statusbar
        self.time_label = QLabel()
        self.right_label = QLabel("Right Section")

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # Update every second
        self.statusbar.addWidget(self.time_label)
        self.statusbar.addPermanentWidget(self.right_label)

    def update_time(self):
        current_time = QDateTime.currentDateTime().toString("dd MMM yyyy | hh:mm:ss AP")
        self.time_label.setText(f'MB LABS | {current_time}')

    def update_status_bar(self, status):
        self.right_label.setText(status)