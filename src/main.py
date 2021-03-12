from mainUI import Ui_MainWindow
from errorPopup import Ui_Dialog
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QTableWidget, QShortcut, QDialog
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QKeySequence, QFont
from dictionary import *
from requests import exceptions
import webbrowser

langFamily = ["ko", "en", "zh", "ja"]


class ErrorPopup(QDialog):
    def __init__(self, message: str):
        super(ErrorPopup, self).__init__()
        self.popup = Ui_Dialog()
        self.popup.setupUi(self)
        self.popup.textBrowser.setText(message)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.URLMap = dict()
        self.rowCount = 0
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.MainTable.setEditTriggers(QTableWidget.NoEditTriggers)
        self.ui.MainTable.setRowCount(30)
        self.ui.queryEdit.setFocus()
        self.ui.MainTable.hideColumn(2)
        self.ui.loadMoreButton.setDisabled(True)

        self.page = 0
        self.dict_obj = None

        query_key = QShortcut(QKeySequence("Ctrl+q"), self)
        ko_key = QShortcut(QKeySequence("Ctrl+1"), self)
        en_key = QShortcut(QKeySequence("Ctrl+2"), self)
        zh_key = QShortcut(QKeySequence("Ctrl+3"), self)
        ja_key = QShortcut(QKeySequence("Ctrl+4"), self)

        query_key.activated.connect(self.set_focus_on_search)
        ko_key.activated.connect(lambda: self.switch_lang(0))
        en_key.activated.connect(lambda: self.switch_lang(1))
        zh_key.activated.connect(lambda: self.switch_lang(2))
        ja_key.activated.connect(lambda: self.switch_lang(3))

        self.ui.MainTable.cellDoubleClicked.connect(self.open_in_web_browser)
        self.ui.queryEdit.returnPressed.connect(lambda: self.first_query(langFamily[self.ui.LangBox.currentIndex()],
                                                                         self.ui.queryEdit.text()))
        self.ui.searchButton.clicked.connect(lambda: self.first_query(langFamily[self.ui.LangBox.currentIndex()],
                                                                      self.ui.queryEdit.text()))
        self.ui.loadMoreButton.clicked.connect(self.load_more)

    def first_query(self, lang: str, query: str):
        if query != "":
            self.ui.loadMoreButton.setDisabled(False)
            self.rowCount = 0
            del self.dict_obj
            self.dict_obj = Dictionary()
            self.ui.MainTable.setRowCount(0)
            self.ui.MainTable.clearContents()
            try:
                self.dict_obj.load_first_page(lang, query)
                self.print_on_table(self.dict_obj.pages[0])
            except exceptions.ConnectionError:
                a = ErrorPopup("데이터를 받아올 수 없습니다. 인터넷을 확인하세요.")
                a.exec_()
            self.ui.MainTable.scrollToTop()
        else:
            pass

    def print_on_table(self, page: Page):
        # 테이블 크기, 행 가시성
        if self.dict_obj.lang == "zh":
            self.ui.MainTable.showColumn(2)
            self.ui.MainTable.setColumnWidth(2, 145)
            font = QFont()
            font.setPointSize(15)
            self.ui.MainTable.setFont(font)
        else:
            self.ui.MainTable.hideColumn(2)
            font = QFont()
            font.setPointSize(11)
            self.ui.MainTable.setFont(font)
        word_column = 0
        pos_column = 1
        traditional_zh = 2
        mean_column = 3

        self.ui.MainTable.setRowCount(self.ui.MainTable.rowCount() + self.count_meanings(page))
        for i in range(len(page.words)):
            current_word = page.words[i]
            if current_word.num is not None:    # 단어를 테이블에 표시
                self.ui.MainTable.setItem(self.rowCount, word_column,
                                          QTableWidgetItem(current_word.word + current_word.num))
            else:
                self.ui.MainTable.setItem(self.rowCount, word_column, QTableWidgetItem(current_word.word))
            if self.dict_obj.lang == "zh" and current_word.traditional_zh is not None:  # 중국어일때 번체 표시
                self.ui.MainTable.setItem(self.rowCount, traditional_zh, QTableWidgetItem(current_word.traditional_zh))
            self.URLMap[self.rowCount] = current_word.word_url
            for j in range(len(current_word.mean.keys())):
                if list(current_word.mean.keys())[j] is None:   # json 에서 품사가 Null 일때 관용구로 표시
                    current_word_part_of_speech = "관용구"
                else:
                    current_word_part_of_speech = str(list(current_word.mean.keys())[j])
                for dict_value_index in range(len(current_word.mean[list(current_word.mean.keys())[j]])):
                    if "(Abbr.)" in current_word.mean[list(current_word.mean.keys())[j]][dict_value_index]:  # 뜻 중에 (Abbr.)이 있으면 약어로 표시
                        current_word_part_of_speech = "약어"
                self.ui.MainTable.setItem(self.rowCount, pos_column, QTableWidgetItem(current_word_part_of_speech))
                if list(current_word.mean.keys())[j] is None:   # 의미를 테이블에 표시
                    word_dict_index = None
                else:
                    word_dict_index = str(list(current_word.mean.keys())[j])
                for k in range(len(current_word.mean[word_dict_index])):
                    self.ui.MainTable.setItem(self.rowCount, mean_column,
                                              QTableWidgetItem(str(current_word.mean[word_dict_index][k])))
                    self.rowCount = self.rowCount + 1
        self.page += 1

    @staticmethod
    def count_meanings(page: Page):
        count = 0
        for word_count in range(len(page.words)):
            for part_of_speech in page.words[word_count].mean.keys():
                for meanings in range(len(page.words[word_count].mean[part_of_speech])):
                    count += 1
        return count

    @pyqtSlot()
    def load_more(self):
        self.dict_obj.load_next_page()
        self.print_on_table(self.dict_obj.pages[self.page])

    def switch_lang(self, lang: int):
        self.ui.LangBox.setCurrentIndex(lang)

    def set_focus_on_search(self):
        self.ui.queryEdit.setFocus()
        self.ui.queryEdit.selectAll()

    def open_in_web_browser(self):
        if self.ui.MainTable.currentColumn() == 0:
            try:
                webbrowser.open(self.URLMap[self.ui.MainTable.currentRow()], 1)
            except KeyError:
                pass


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
