import sys
from PyQt5.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QScrollBar

app = QApplication(sys.argv)

table = QTableWidget()
table.setColumnCount(2)
table.setRowCount(5)

for row in range(5):
    for column in range(2):
        item = QTableWidgetItem("Row %d, Column %d" % (row, column))
        table.setItem(row, column, item)

scrollbar = QScrollBar()
scrollbar.setOrientation(0)  # Set orientation to horizontal

layout = QVBoxLayout()
layout.addWidget(table)
layout.addWidget(scrollbar)

widget = QWidget()
widget.setLayout(layout)

widget.show()
sys.exit(app.exec_())
