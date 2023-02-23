import sys, os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *   

class MainPage(QMainWindow):
    def __init__(self):
        super().__init__()
        self.mdi = QMdiArea()
        self.mdi.setFixedSize(1000, 400)
        self.mdi.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.mdi.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setWindowTitle("Sample Programme")
        self.setGeometry(100, 100, 1600, 600)
        self.Ui()

    def Ui(self):
        self.btn1 = QPushButton("Country")
        self.btn1.setFixedSize(100, 30)
        self.btn1.clicked.connect(self.countrypage)
        self.left_layout = QVBoxLayout()
        self.right_layout = QHBoxLayout()
        self.main_layout = QHBoxLayout()
        self.left_layout.setContentsMargins(3, 5, 5, 3)
        self.left_layout.addWidget(self.btn1)
        self.left_layout.addStretch()
        self.right_layout.addWidget(self.mdi)
        self.main_layout.setSpacing(5)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addLayout(self.left_layout)
        self.main_layout.addLayout(self.right_layout)
        self.main_layout.addStretch()
        widget = QWidget()
        widget.setLayout(self.main_layout)
        self.setCentralWidget(widget)

    def countrypage(self):
        page = Countrypage()
        subwindow = self.mdi.addSubWindow(page)
        subwindow.setWindowTitle("Create Country")
        subwindow.setFixedWidth(300)
        page.btn_close.clicked.connect(self.subwindowclose)
        page.btn_new.clicked.connect(self.countrypage)
        subwindow.show()
        self.mdi.cascadeSubWindows()

    def subwindowclose(self):
        print("close activated from mdi programme")
        current = self.mdi.activeSubWindow()
        if current is not None:
            self.mdi.activatePreviousSubWindow()
            previous = self.mdi.activeSubWindow()
            if previous is not None:
                previous.widget().update_fields(current.widget())
            current.close()


class Countrypage(QWidget):
    def __init__(self):
        super().__init__()
        self.btn_close = QPushButton("Close")
        self.btn_new = QPushButton("New")
        self.tb_country = QLineEdit()
        self.tb_continent = QLineEdit()
        self.form_layout = QFormLayout()
        self.form_layout.addRow("Country", self.tb_country)
        self.form_layout.addRow("Continent", self.tb_continent)
        self.form_layout.addRow("", self.btn_close)
        self.form_layout.addRow("", self.btn_new)
        self.setLayout(self.form_layout)

    def update_fields(self, other):
        if isinstance(other, Countrypage):
            self.tb_country.setText(other.tb_country.text())
            self.tb_continent.setText(other.tb_continent.text())
        else:
            raise TypeError('invalid page type')


if __name__ == "__main__":

    app = QApplication(sys.argv)
    mainwindow = MainPage()
    app.setStyle("Windows")
    mainwindow.show()
    sys.exit(app.exec_())