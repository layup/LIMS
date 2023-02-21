# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'tester.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ICP(object):
    def setupUi(self, ICP):
        ICP.setObjectName("ICP")
        ICP.resize(847, 678)
        self.verticalLayout = QtWidgets.QVBoxLayout(ICP)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.Header = QtWidgets.QWidget(ICP)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Header.sizePolicy().hasHeightForWidth())
        self.Header.setSizePolicy(sizePolicy)
        self.Header.setMaximumSize(QtCore.QSize(16777215, 80))
        self.Header.setStyleSheet("background-color: rgb(255, 215, 0);")
        self.Header.setObjectName("Header")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.Header)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_11 = QtWidgets.QLabel(self.Header)
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(75)
        self.label_11.setFont(font)
        self.label_11.setObjectName("label_11")
        self.gridLayout_2.addWidget(self.label_11, 0, 0, 1, 1)
        self.label_12 = QtWidgets.QLabel(self.Header)
        self.label_12.setObjectName("label_12")
        self.gridLayout_2.addWidget(self.label_12, 2, 0, 1, 1)

        self.uploadFile = QtWidgets.QPushButton(self.Header)
        self.uploadFile.setMaximumSize(QtCore.QSize(100, 16777215))
        self.uploadFile.setObjectName("uploadFile")

    
        #make the button do the thing in here, doesn't matter 
        self.uploadFile.clicked.connect(lambda: print("hello World"))
        
        self.gridLayout_2.addWidget(self.uploadFile, 0, 1, 1, 1)
        self.verticalLayout.addWidget(self.Header)
        self.Body = QtWidgets.QWidget(ICP)
        self.Body.setStyleSheet("background: rgb(224, 229, 229)")
        self.Body.setObjectName("Body")
        self.gridLayout = QtWidgets.QGridLayout(self.Body)
        self.gridLayout.setObjectName("gridLayout")
        self.widget_2 = QtWidgets.QWidget(self.Body)
        self.widget_2.setObjectName("widget_2")
        self.label = QtWidgets.QLabel(self.widget_2)
        self.label.setGeometry(QtCore.QRect(10, 10, 121, 16))
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.widget_2, 0, 0, 1, 1)
        self.widget_4 = QtWidgets.QWidget(self.Body)
        self.widget_4.setObjectName("widget_4")
        self.label_2 = QtWidgets.QLabel(self.widget_4)
        self.label_2.setGeometry(QtCore.QRect(10, 10, 141, 16))
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.widget_4, 0, 1, 1, 1)
        self.verticalLayout.addWidget(self.Body)

        self.retranslateUi(ICP)
        QtCore.QMetaObject.connectSlotsByName(ICP)

    def retranslateUi(self, ICP):
        _translate = QtCore.QCoreApplication.translate
        ICP.setWindowTitle(_translate("ICP", "Form"))
        self.label_11.setText(_translate("ICP", "ICP "))
        self.label_12.setText(_translate("ICP", "JobNum: "))
        self.uploadFile.setText(_translate("ICP", "Upload File"))
        self.label.setText(_translate("ICP", "Ready for Creation"))
        self.label_2.setText(_translate("ICP", "Generated Reports"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ICP = QtWidgets.QWidget()
    ui = Ui_ICP()
    ui.setupUi(ICP)
    ICP.show()
    sys.exit(app.exec_())
