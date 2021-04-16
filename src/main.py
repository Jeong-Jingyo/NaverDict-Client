import multiprocessing
import shutil
import webbrowser
from os.path import exists

from PyQt5.QtCore import pyqtSlot, QSize
from PyQt5.QtGui import QKeySequence, QFont, QIcon, QFontMetrics
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QTableWidget, QShortcut, QDialog, QPushButton, \
    QLabel, QSizePolicy
from requests import exceptions

import resources_rc
from dictionary import *
from errorPopup_ui import Ui_Dialog as Ui_errorPopup
from main_ui import Ui_MainWindow

langFamily = ["ko", "en", "zh", "ja"]
kr_langFamily = {"ko": "국어", "en": "영어", "zh": "중국어", "ja": "일본어"}
old_kr_font = QFont("맑은 고딕", 15)
old_kr_query_font = QFont("맑은 고딕", 14)
default_font = QFont("맑은 고딕", 14)
query_font = QFont("맑은 고딕", 13)


class QPushButton(QPushButton):
    def __init__(self, *__args):
        super(QPushButton, self).__init__(*__args)
        self.size = self.font().pointSize()
        self.icon_size = (self.iconSize().width(), self.iconSize().height())
        self.pressed.connect(self.decrease_size)
        self.released.connect(self.reset_size)

    def decrease_size(self):
        font = QFont()
        font.setPointSize(self.size - 1)
        self.setFont(font)
        self.setIconSize(QSize(self.icon_size[0] - 1, self.icon_size[1] - 1))

    def reset_size(self):
        font = QFont()
        font.setPointSize(self.size)
        self.setFont(font)
        self.setIconSize(QSize(self.icon_size[0], self.icon_size[1]))


class ErrorPopup(QDialog):
    def __init__(self, message: str):
        super(ErrorPopup, self).__init__()
        self.popup = Ui_errorPopup()
        self.popup.setupUi(self)
        self.popup.textBrowser.setText(message)


class PronunciationTable(QTableWidget):
    def __init__(self, word: Word):
        length = 0
        printed = 0
        for index in range(len(word.pronounces)):
            if (word.pronounces[index][1][0] is not None) or (word.pronounces[index][1][1] != ""):
                length += 1
        super(PronunciationTable, self).__init__(1, length)
        self.horizontalHeader().setVisible(False)
        self.verticalHeader().setVisible(False)
        for index in range(len(word.pronounces)):
            if (word.pronounces[index][1][0] is not None) or (word.pronounces[index][1][1] != ""):
                if word.pronounces[index][1][1] != "":
                    self.setCellWidget(0, printed, PronounceButton(word, index))
                else:
                    self.setCellWidget(0, printed, PronounceLabel(word, index))
                printed += 1
        self.resizeColumnsToContents()
        self.setShowGrid(False)
        self.setFrameStyle(0)
        self.setContentsMargins(0, 0, 0, 1)


class PronounceButton(QPushButton):
    def __init__(self, word: Word, index: int):
        if word.pronounces[index][0] is not None:
            pron_locale = word.pronounces[index][0]
        else:
            pron_locale = ""
        if word.pronounces[index][1][0] is not None:
            pron = delete_html(word.pronounces[index][1][0])
        else:
            pron = ""
        super().__init__(QIcon(":/images/play-sound.svg"), pron_locale + pron)
        if word.pronounces[index][1][1] == "":
            self.setDisabled(True)
        self.clicked.connect(lambda: word.download_pronunciation(index))
        self.setFixedHeight(35)

    @staticmethod
    @pyqtSlot()
    def pronounce(word: Word, index):
        p = multiprocessing.Process(target=word.download_pronunciation, args=(index,))
        p.start()


class PronounceLabel(QLabel):
    def __init__(self, word: Word, index: int):
        if word.pronounces[index][0] is not None:
            pron_locale = word.pronounces[index][0]
        else:
            pron_locale = ""
        if word.pronounces[index][1][0] is not None:
            pron = delete_html(word.pronounces[index][1][0]) + "  "
        else:
            pron = ""
        super().__init__(pron_locale + pron)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setFixedHeight(35)


class MainWindow(QMainWindow):
    word_column = 0
    pronunciation_column = 1
    pos_column = 2
    traditional_zh_column = 3
    mean_column = 4

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.queryEdit.setFocus()
        self.setStyleSheet(open("stylesheets/light/main-stylesheet.qss").read())
        self.page = 0
        self.dict_obj = None
        self.URLMap = dict()
        self.rowCount = 0
        self.ui.splitter.handle(1).setDisabled(True)
        self.ui.splitter.handle(2).setDisabled(True)

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

        self.ui.LangBox.currentIndexChanged.connect(lambda: self.change_font(langFamily[self.ui.LangBox.currentIndex()]))
        self.ui.queryEdit.returnPressed.connect(lambda: self.first_query(langFamily[self.ui.LangBox.currentIndex()],
                                                                         self.ui.queryEdit.text()))
        self.ui.searchButton.clicked.connect(lambda: self.first_query(langFamily[self.ui.LangBox.currentIndex()],
                                                                      self.ui.queryEdit.text()))
        self.ui.centralwidget.setVisible(True)

    def first_query(self, lang: str, query: str):
        if query != "":
            self.ui.queryEdit.setFixedHeight(40)
            self.ui.showTable(self)
            self.ui.MainTable.setEditTriggers(QTableWidget.NoEditTriggers)
            self.ui.MainTable.hideColumn(self.pronunciation_column)
            self.ui.MainTable.hideColumn(self.traditional_zh_column)
            self.ui.MainTable.cellDoubleClicked.connect(self.open_in_web_browser)
            self.ui.loadMoreButton.clicked.connect(self.load_more)

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

    def query_anim(self):
        pass

    def print_on_table(self, page: Page):
        # 테이블 크기, 행 가시성
        if self.dict_obj.lang == "zh":
            self.ui.MainTable.showColumn(self.traditional_zh_column)
            self.ui.MainTable.setColumnWidth(self.traditional_zh_column, 145)
            self.ui.MainTable.setFont(old_kr_font)
        else:
            self.ui.MainTable.hideColumn(self.traditional_zh_column)
            self.ui.MainTable.setFont(old_kr_font)

        self.ui.MainTable.setRowCount(self.ui.MainTable.rowCount() + self.count_meanings(page))
        for i in range(len(page.words)):
            current_word = page.words[i]
            word_start_pos = self.rowCount
            if current_word.num is not None:    # 단어를 테이블에 표시
                self.ui.MainTable.setItem(self.rowCount, self.word_column,
                                          QTableWidgetItem(current_word.word + current_word.num))
            else:
                self.ui.MainTable.setItem(self.rowCount, self.word_column, QTableWidgetItem(current_word.word))
            if self.dict_obj.lang == "zh" and current_word.traditional_zh is not None:  # 중국어일때 번체 표시
                self.ui.MainTable.setItem(self.rowCount, self.traditional_zh_column, QTableWidgetItem(current_word.traditional_zh))
            if current_word.dict_name != "위키낱말사전" and current_word.dict_name != "Urbandictionary":
                self.URLMap[self.rowCount] = current_word.word_url

            # 발음 버튼
            if len(current_word.pronounces) != 0:
                for i in current_word.pronounces:
                    self.ui.MainTable.setItem(self.rowCount, self.pronunciation_column, QTableWidgetItem(i[1][0]))
                self.ui.MainTable.setSpan(self.rowCount, self.pronunciation_column, 1, 4)
                self.ui.MainTable.setCellWidget(self.rowCount, self.pronunciation_column, PronunciationTable(current_word))
                self.rowCount += 1

            # 의미
            mean_start_pos = self.rowCount
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
                    self.rowCount += 1
                self.ui.MainTable.setSpan(mean_start_pos, self.pos_column, self.rowCount - mean_start_pos, 1)
            self.ui.MainTable.setSpan(word_start_pos, self.word_column, self.rowCount - word_start_pos, 1)
        self.page += 1

    def closeEvent(self, a0) -> None:
        if exists("./cache"):
            shutil.rmtree("./cache")

    def change_font(self, lang: str):
        try:
            if lang == "ko":
                self.ui.MainTable.setFont(old_kr_font)
                self.ui.queryEdit.setFont(old_kr_query_font)
            else:
                self.ui.MainTable.setFont(default_font)
                self.ui.queryEdit.setFont(query_font)
        except AttributeError:
            self.ui.queryEdit.setFont(old_kr_font)
            self.ui.queryEdit.setFont(default_font)

    @staticmethod
    def count_meanings(page: Page):
        count = 0
        for word_count in range(len(page.words)):
            count += 1
            for part_of_speech in page.words[word_count].mean.keys():
                for meanings in range(len(page.words[word_count].mean[part_of_speech])):
                    count += 1
            if len(page.words[word_count].pronounces) == 0:
                count -= 1
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


def delete_html(text: str):
    html_regex = re.compile("<[^<|>]*>")
    html_list = html_regex.findall(text)
    temp_text = text
    for html in html_list:
        temp_text = temp_text.replace(html, "")
    return temp_text


if __name__ == '__main__':
    resources_rc.qInitResources()
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.setFont(old_kr_font)
    window.ui.queryEdit.setFont(old_kr_query_font)
    app.exec_()
