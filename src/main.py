from mainUI import Ui_MainWindow
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QTableWidget, QShortcut
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QKeySequence, QFont
from dictionary import *

langFamily = ["ko", "en", "zh", "ja"]


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.rowCount = 0
        self.temp_rowCount = 0
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.MainTable.setEditTriggers(QTableWidget.NoEditTriggers)
        self.ui.MainTable.setRowCount(30)
        self.ui.queryEdit.setFocus()
        self.ui.MainTable.hideColumn(2)

        self.page = 0
        self.dict_obj = Dictionary()

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

        self.ui.queryEdit.returnPressed.connect(lambda: self.set_word_wrapper(
            langFamily[self.ui.LangBox.currentIndex()], self.ui.queryEdit.text(), 1, browser_header))
        self.ui.searchButton.clicked.connect(lambda: self.set_word_wrapper(
            langFamily[self.ui.LangBox.currentIndex()], self.ui.queryEdit.text(), 1, browser_header))
        self.ui.loadMoreButton.clicked.connect(lambda: self.load_more(browser_header))

    def set_word_wrapper(self, lang: str, query: str, page: int, header: dict):
        if query != "":
            self.ui.MainTable.clearContents()
            self.dict_obj.words = list()
            self.temp_rowCount = 0
            self.page = page
            self.set_word(lang, query, page, header)
            self.ui.MainTable.scrollToTop()
        else:
            pass

    @pyqtSlot()
    def set_word(self, lang: str, query: str, page: int, header: dict):
        self.rowCount = 0
        self.temp_rowCount = 0
        removed_word_amount = 0
        word_start_index, word_end_index = self.dict_obj.get_word(lang, query, page, header)

        for i in range(word_start_index, word_end_index):
            self.dict_obj.words[i] = self.dict_obj.filter_word(self.dict_obj.words[i])

        while None in self.dict_obj.words:
            self.dict_obj.words.remove(None)
            removed_word_amount += 1

        # 중국어 번체 받아오기
        for i in range(word_start_index, word_end_index - removed_word_amount):
            if self.dict_obj.lang == "zh" and len(self.dict_obj.words[i].word) < 2:
                self.dict_obj.words[i].get_traditional_zh(browser_header)

        for i in range(len(self.dict_obj.words)):
            temp_current_word = self.dict_obj.words[i]
            for j in range(len(temp_current_word.mean.keys())):
                if list(temp_current_word.mean.keys())[j] is None:
                    temp_word_dict_index = None
                else:
                    temp_word_dict_index = str(list(temp_current_word.mean.keys())[j])
                for k in range(len(temp_current_word.mean[temp_word_dict_index])):
                    self.temp_rowCount = self.temp_rowCount + 1

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

        self.ui.MainTable.setRowCount(self.temp_rowCount)

        for i in range(len(self.dict_obj.words)):
            current_word = self.dict_obj.words[i]
            if current_word.num is not None:    # 단어를 테이블에 표시
                self.ui.MainTable.setItem(self.rowCount, word_column,
                                          QTableWidgetItem(current_word.word + current_word.num))
            else:
                self.ui.MainTable.setItem(self.rowCount, word_column, QTableWidgetItem(current_word.word))
            if self.dict_obj.lang == "zh" and current_word.traditional_zh is not None:  # 중국어일때 번체 표시
                self.ui.MainTable.setItem(self.rowCount, traditional_zh, QTableWidgetItem(current_word.traditional_zh))
            for j in range(len(current_word.mean.keys())):
                if list(current_word.mean.keys())[j] is None:   # json 에서 품사가 Null 일때 관용구로 표시
                    current_word_part_of_speech = "관용구"
                else:
                    current_word_part_of_speech = str(list(current_word.mean.keys())[j])
                for dict_value_index in range(len(current_word.mean[list(current_word.mean.keys())[j]])):
                    if "(Abbr.)" in current_word.mean[list(current_word.mean.keys())[j]][dict_value_index]: # 뜻 중에 (Abbr.)이 있으면 약어로 표시
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

    @pyqtSlot()
    def load_more(self, header: dict):
        self.page = self.page + 1
        self.set_word(self.dict_obj.lang, self.dict_obj.query, self.page, header)

    def switch_lang(self, lang: int):
        self.ui.LangBox.setCurrentIndex(lang)

    def set_focus_on_search(self):
        self.ui.queryEdit.setFocus()
        self.ui.queryEdit.selectAll()



if __name__ == '__main__':
    browser_header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
                                    "Chrome/88.0.4324.150 Safari/537.36"}  # 크롬에서 복사함
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
