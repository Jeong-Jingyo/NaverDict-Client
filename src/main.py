from main_ui import Ui_MainWindow
from errorPopup_ui import Ui_Dialog as Ui_errorPopup
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QTableWidget, QShortcut, QDialog
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QKeySequence, QFont
from dictionary import *
from requests import exceptions
import webbrowser

langFamily = ["ko", "en", "zh", "ja"]
kr_langFamily = {"ko": "국어", "en": "영어", "zh": "중국어", "ja": "일본어"}


class ErrorPopup(QDialog):
    def __init__(self, message: str):
        super(ErrorPopup, self).__init__()
        self.popup = Ui_errorPopup()
        self.popup.setupUi(self)
        self.popup.textBrowser.setText(message)


class MainWindow(QMainWindow):
    word_column = 0
    pronunciation_column = 1
    pos_column = 2
    traditional_zh_column = 3
    mean_column = 4
    default_font = QFont()
    default_font.setFamily("나눔바른고딕 옛한글")
    default_font.setPointSize(12)

    def __init__(self):
        super(MainWindow, self).__init__()
        self.URLMap = dict()
        self.rowCount = 0
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.MainTable.setEditTriggers(QTableWidget.NoEditTriggers)
        self.ui.MainTable.setRowCount(30)
        self.ui.queryEdit.setFocus()
        self.ui.MainTable.hideColumn(self.pronunciation_column)
        self.ui.MainTable.hideColumn(self.traditional_zh_column)
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
            self.page = 0
            del self.dict_obj
            self.dict_obj = Dictionary()
            self.ui.MainTable.setRowCount(0)
            self.ui.MainTable.clearContents()
            self.URLMap = dict()
            try:
                self.dict_obj.load_first_page(lang, query)
                self.print_on_table(self.dict_obj.pages[0])
                self.ui.MainTable.scrollToTop()
                self.setWindowTitle("\"" + query + "\"의 " + kr_langFamily[lang] + "사전 검색 결과: NaverDict-Client")
            except exceptions.ConnectionError:
                a = ErrorPopup("데이터를 받아올 수 없습니다. 인터넷을 확인하세요.")
                a.exec_()
        else:
            pass

    def print_on_table(self, page: Page):
        # 테이블 크기, 행 가시성
        if self.dict_obj.lang == "zh":
            self.ui.MainTable.showColumn(self.traditional_zh_column)
            self.ui.MainTable.setColumnWidth(2, 145)
            self.ui.MainTable.setFont(self.default_font)
        else:
            self.ui.MainTable.hideColumn(self.traditional_zh_column)
            self.ui.MainTable.setFont(self.default_font)

        self.ui.MainTable.setRowCount(self.ui.MainTable.rowCount() + self.count_meanings(page))
        for i in range(len(page.words)):
            current_word = page.words[i]
            if current_word.num is not None:    # 단어를 테이블에 표시
                self.ui.MainTable.setItem(self.rowCount, self.word_column,
                                          QTableWidgetItem(current_word.word + current_word.num))
            else:
                self.ui.MainTable.setItem(self.rowCount, self.word_column, QTableWidgetItem(current_word.word))
            if self.dict_obj.lang == "zh" and current_word.traditional_zh_column is not None:  # 중국어일때 번체 표시
                self.ui.MainTable.setItem(self.rowCount, self.traditional_zh_column, QTableWidgetItem(current_word.traditional_zh_column))
            if current_word.dict_name != "위키낱말사전" and current_word.dict_name != "Urbandictionary":
                self.URLMap[self.rowCount] = current_word.word_url
            for j in range(len(current_word.mean.keys())):
                if list(current_word.mean.keys())[j] is None:   # json 에서 품사가 Null 일때 관용구로 표시
                    current_word_part_of_speech = "관용구"
                else:
                    current_word_part_of_speech = str(list(current_word.mean.keys())[j])
                for dict_value_index in range(len(current_word.mean[list(current_word.mean.keys())[j]])):
                    if "(Abbr.)" in current_word.mean[list(current_word.mean.keys())[j]][dict_value_index]:  # 뜻 중에 (Abbr.)이 있으면 약어로 표시
                        current_word_part_of_speech = "약어"
                self.ui.MainTable.setItem(self.rowCount, self.pos_column, QTableWidgetItem(current_word_part_of_speech))
                if list(current_word.mean.keys())[j] is None:   # 의미를 테이블에 표시
                    word_dict_index = None
                else:
                    word_dict_index = str(list(current_word.mean.keys())[j])
                for k in range(len(current_word.mean[word_dict_index])):
                    self.ui.MainTable.setItem(self.rowCount, self.mean_column,
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
