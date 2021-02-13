# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main-table.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1200, 600)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("favicon.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.MainTable = QtWidgets.QTableWidget(self.centralwidget)
        self.MainTable.setEnabled(True)
        self.MainTable.setAcceptDrops(False)
        self.MainTable.setInputMethodHints(QtCore.Qt.ImhNone)
        self.MainTable.setLineWidth(5)
        self.MainTable.setObjectName("MainTable")
        self.MainTable.setColumnCount(3)
        self.MainTable.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.MainTable.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.MainTable.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.MainTable.setHorizontalHeaderItem(2, item)
        self.MainTable.horizontalHeader().setStretchLastSection(True)
        self.MainTable.verticalHeader().setVisible(False)
        self.gridLayout.addWidget(self.MainTable, 1, 0, 1, 1)
        self.splitter = QtWidgets.QSplitter(self.centralwidget)
        self.splitter.setMinimumSize(QtCore.QSize(0, 30))
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.LangBox = QtWidgets.QComboBox(self.splitter)
        self.LangBox.setObjectName("LangBox")
        self.LangBox.addItem("")
        self.LangBox.addItem("")
        self.LangBox.addItem("")
        self.LangBox.addItem("")
        self.queryEdit = QtWidgets.QLineEdit(self.splitter)
        self.queryEdit.setInputMethodHints(QtCore.Qt.ImhNone)
        self.queryEdit.setText("")
        self.queryEdit.setFrame(True)
        self.queryEdit.setCursorPosition(0)
        self.queryEdit.setCursorMoveStyle(QtCore.Qt.LogicalMoveStyle)
        self.queryEdit.setClearButtonEnabled(True)
        self.queryEdit.setObjectName("queryEdit")
        self.searchButton = QtWidgets.QPushButton(self.splitter)
        self.searchButton.setObjectName("searchButton")
        self.gridLayout.addWidget(self.splitter, 0, 0, 1, 1)
        self.loadMoreButton = QtWidgets.QPushButton(self.centralwidget)
        self.loadMoreButton.setMinimumSize(QtCore.QSize(0, 30))
        self.loadMoreButton.setObjectName("loadMoreButton")
        self.gridLayout.addWidget(self.loadMoreButton, 2, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setTabOrder(self.queryEdit, self.LangBox)
        MainWindow.setTabOrder(self.LangBox, self.searchButton)
        MainWindow.setTabOrder(self.searchButton, self.MainTable)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "NaverDict-Client"))
        item = self.MainTable.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "단어"))
        item = self.MainTable.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "품사"))
        item = self.MainTable.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "의미"))
        self.LangBox.setItemText(0, _translate("MainWindow", "국어"))
        self.LangBox.setItemText(1, _translate("MainWindow", "영어"))
        self.LangBox.setItemText(2, _translate("MainWindow", "중국어"))
        self.LangBox.setItemText(3, _translate("MainWindow", "일본어"))
        self.searchButton.setText(_translate("MainWindow", "검색"))
        self.loadMoreButton.setText(_translate("MainWindow", "더 불러오기"))
