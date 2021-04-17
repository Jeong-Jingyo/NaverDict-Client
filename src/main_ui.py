# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './main-table.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


default_font = QtGui.QFont("맑은 고딕", 14)
stylesheet = open("stylesheets/light/main-stylesheet.qss").read()

class QPushButton(QtWidgets.QPushButton):
    def __init__(self, *__args):
        self.size = None
        super(QPushButton, self).__init__(*__args)
        self.icon_size = (self.iconSize().width(), self.iconSize().height())
        self.pressed.connect(self.decrease_size)
        self.released.connect(self.reset_size)

    def decrease_size(self):
        self.size = self.font().pointSize()
        font = QtGui.QFont()
        font.setPointSize(self.size - 1)
        self.setFont(font)
        self.setIconSize(QtCore.QSize(self.icon_size[0] - 1, self.icon_size[1] - 1))

    def reset_size(self):
        font = QtGui.QFont()
        font.setPointSize(self.size)
        self.setFont(font)
        self.setIconSize(QtCore.QSize(self.icon_size[0], self.icon_size[1]))


class Ui_MainWindow(object):
    def setupUi(self, MainWindow, scale: int):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(2000, 400)
        MainWindow.setFont(default_font)
        MainWindow.move(300, 100)
        MainWindow.setStyleSheet(stylesheet)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/favicon.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon.addPixmap(QtGui.QPixmap(":/images/favicon.ico"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.splitter = QtWidgets.QSplitter(self.centralwidget)
        self.splitter.setMinimumSize(QtCore.QSize(0, 30))
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.LangBox = QtWidgets.QComboBox(self.splitter)
        self.LangBox.setFont(default_font)
        self.LangBox.setObjectName("LangBox")
        self.LangBox.addItem("")
        self.LangBox.addItem("")
        self.LangBox.addItem("")
        self.LangBox.addItem("")
        self.LangBox.setMaximumWidth(200)
        policy = QtWidgets.QSizePolicy()
        policy.Expanding = True
        self.LangBox.setSizePolicy(policy)
        self.queryEdit = QtWidgets.QLineEdit(self.splitter)
        self.queryEdit.setFont(default_font)
        self.queryEdit.setInputMethodHints(QtCore.Qt.ImhNone)
        self.queryEdit.setText("")
        self.queryEdit.setFrame(True)
        self.queryEdit.setCursorPosition(0)
        self.queryEdit.setCursorMoveStyle(QtCore.Qt.LogicalMoveStyle)
        self.queryEdit.setClearButtonEnabled(True)
        self.queryEdit.setObjectName("queryEdit")
        self.searchButton = QPushButton(self.splitter)
        self.searchButton.setFont(default_font)
        self.searchButton.setObjectName("searchButton")
        self.gridLayout.addWidget(self.splitter, 0, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.queryEdit.setFixedHeight(70)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setTabOrder(self.queryEdit, self.LangBox)
        MainWindow.setTabOrder(self.LangBox, self.searchButton)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "NaverDict-Client"))
        self.LangBox.setItemText(0, _translate("MainWindow", "국어"))
        self.LangBox.setItemText(1, _translate("MainWindow", "영어"))
        self.LangBox.setItemText(2, _translate("MainWindow", "중국어"))
        self.LangBox.setItemText(3, _translate("MainWindow", "일본어"))
        self.searchButton.setText(_translate("MainWindow", "검색"))

    def showTable(self, MainWindow, scale: int):
        MainWindow.resize(2000, 1500)
        self.MainTable = QtWidgets.QTableWidget(self.centralwidget)
        self.MainTable.setEnabled(True)
        self.MainTable.setFont(default_font)
        self.MainTable.setAcceptDrops(False)
        self.MainTable.setInputMethodHints(QtCore.Qt.ImhNone)
        self.MainTable.setLineWidth(5)
        self.MainTable.setObjectName("MainTable")
        self.MainTable.setColumnCount(5)
        self.MainTable.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.MainTable.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        item.setForeground(brush)
        self.MainTable.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.MainTable.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.MainTable.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.MainTable.setHorizontalHeaderItem(4, item)
        self.MainTable.horizontalHeader().setVisible(True)
        self.MainTable.horizontalHeader().setStretchLastSection(True)
        self.MainTable.verticalHeader().setVisible(False)
        self.gridLayout.addWidget(self.MainTable, 1, 0, 1, 1)
        self.MainTable.setFocusPolicy(QtCore.Qt.NoFocus)
        self.MainTable.horizontalScrollBar().setStyleSheet("")
        self.MainTable.setFont(default_font)
        self.MainTable.horizontalHeader().setFont(default_font)

        self.loadMoreButton = QPushButton(self.centralwidget)
        self.loadMoreButton.setMinimumSize(QtCore.QSize(0, 30))
        self.loadMoreButton.setObjectName("loadMoreButton")
        self.loadMoreButton.setFixedHeight(35 * scale)
        self.loadMoreButton.setFont(default_font)
        self.gridLayout.addWidget(self.loadMoreButton, 2, 0, 1, 1)

        self.retranslateTable()
        MainWindow.setTabOrder(self.searchButton, self.loadMoreButton)
        MainWindow.setTabOrder(self.loadMoreButton, self.MainTable)

    def retranslateTable(self):
        _translate = QtCore.QCoreApplication.translate
        item = self.MainTable.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "단어"))
        item = self.MainTable.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "발음"))
        item = self.MainTable.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "품사"))
        item = self.MainTable.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "번체/음,훈"))
        item = self.MainTable.horizontalHeaderItem(4)
        item.setText(_translate("MainWindow", "의미"))
        self.loadMoreButton.setText(_translate("MainWindow", "더 불러오기"))


class Ui_errorPopup(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setEnabled(True)
        Dialog.resize(300, 200)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        Dialog.setMinimumSize(QtCore.QSize(300, 200))
        Dialog.setMaximumSize(QtCore.QSize(300, 200))
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(218, 160, 75, 23))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Close)
        self.buttonBox.setObjectName("buttonBox")
        self.textBrowser = QtWidgets.QTextBrowser(Dialog)
        self.textBrowser.setGeometry(QtCore.QRect(10, 10, 281, 141))
        self.textBrowser.setObjectName("textBrowser")
        self.textBrowser.setStyleSheet(stylesheet)
        self.buttonBox.setStyleSheet(stylesheet)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Error"))
        self.textBrowser.setHtml(_translate("Dialog",
                                            "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
                                            "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
                                            "p, li { white-space: pre-wrap; }\n"
                                            "</style></head><body style=\" font-family:\'Gulim\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
                                            "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; "
                                            "-qt-block-indent:0; text-indent:0px; font-family:\'맑은 고딕\'; "
                                            "font-size:11pt;\"><br /></p></body></html>"))


import resources_rc
