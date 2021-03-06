import multiprocessing
import shutil
import webbrowser
from os.path import exists

from requests import exceptions

import resources_rc
from dictionary import *
from main_ui import *

if system() == "Windows":
    from win32 import win32gui, win32print
    from win32.win32api import GetSystemMetrics
    import win32con
    hDC = win32gui.GetDC(0)
    original_size = (win32print.GetDeviceCaps(hDC, win32con.DESKTOPHORZRES), win32print.GetDeviceCaps(hDC, win32con.DESKTOPVERTRES))
    scaled_width = GetSystemMetrics(0)
    screen_scale = int(original_size[0] / scaled_width)

langFamily = ["ko", "en", "zh", "ja"]
kr_langFamily = {"ko": "국어", "en": "영어", "zh": "중국어", "ja": "일본어"}
default_font = QFont("맑은 고딕", 14)


class ErrorPopup(QDialog):
    def __init__(self, message: str):
        super(ErrorPopup, self).__init__()
        self.popup = Ui_errorPopup()
        self.popup.setupUi(self)
        self.popup.textBrowser.setText(message)


class InfoTable(QTableWidget):
    def __init__(self, word: Word):
        length = 0
        printed = 0
        for index in range(len(word.pronounces)):
            length += 1
            if (word.pronounces[index][1][0] is not None) or (word.pronounces[index][1][1] != ""):
                length += 1
            if word.traditional_zh is not None:
                length += 1
        super(InfoTable, self).__init__(1, length)
        self.horizontalHeader().setVisible(False)
        self.verticalHeader().setVisible(False)
        for index in range(len(word.pronounces)):
            if (word.pronounces[index][1][0] is not None) or (word.pronounces[index][1][1] != ""):
                if word.pronounces[index][1][1] != "":
                    self.setCellWidget(0, printed, PronounceButton(word, index, screen_scale))
                else:
                    self.setCellWidget(0, printed, PronunciationLabel(word, index))
                printed += 1
        if word.traditional_zh is not None:
            self.setCellWidget(0, printed, InfoLabel(word.traditional_zh))
            printed += 1
        self.resizeColumnsToContents()
        self.setShowGrid(False)
        self.setFrameStyle(0)
        self.setContentsMargins(0, 0, 0, 1)
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)


class PronounceButton(QPushButton):
    def __init__(self, word: Word, index: int, scale: int):
        if word.pronounces[index][0] is not None:
            pron_locale = word.pronounces[index][0]
        else:
            pron_locale = ""
        if word.pronounces[index][1][0] is not None:
            pron = "[" + delete_html(word.pronounces[index][1][0]) + "]"
        else:
            pron = ""
        super().__init__(QIcon(":/images/play-sound.svg"), pron_locale + pron)
        if word.pronounces[index][1][1] == "":
            self.setDisabled(True)
        self.clicked.connect(lambda: word.pronounce(index))
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.setFont(default_font)

    @staticmethod
    @pyqtSlot()
    def pronounce(word: Word, index):
        p = multiprocessing.Process(target=word.pronounce, args=(index,))
        p.start()


class PronunciationLabel(QLabel):
    def __init__(self, word: Word, index: int):
        if word.pronounces[index][0] is not None:
            pron_locale = word.pronounces[index][0]
        else:
            pron_locale = ""
        if word.pronounces[index][1][0] is not None:
            pron = "[" + delete_html(word.pronounces[index][1][0]) + "]"
        else:
            pron = ""
        super().__init__(pron_locale + pron)
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.MinimumExpanding)
        self.setFont(default_font)
        self.setFixedWidth(self.fontMetrics().width(self.text()) + 10 * screen_scale)


class InfoLabel(QLabel):
    def __init__(self, text: str):
        super().__init__(text)
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.MinimumExpanding)
        self.setFont(default_font)
        self.setFixedWidth(self.fontMetrics().width(self.text()) + 10 * screen_scale)


class MainWindow(QMainWindow):
    word_column = 0
    pos_column = 1
    mean_column = 2

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self, screen_scale, original_size)
        self.ui.queryEdit.setFocus()
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
            if self.ui.isTableVisible is False:
                self.ui.queryEdit.setFixedHeight(40 * screen_scale)
                self.ui.showTable(self, screen_scale, original_size)
                self.ui.MainTable.setEditTriggers(QTableWidget.NoEditTriggers)
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
            self.set_focus_on_search()
        else:
            pass

    def query_anim(self):
        pass

    def print_on_table(self, page: Page):

        self.ui.MainTable.setRowCount(self.ui.MainTable.rowCount() + self.count_rows_to_add(page))
        for i in range(len(page.words)):
            current_word = page.words[i]
            word_start_pos = self.rowCount
            if current_word.num is not None:    # 단어를 테이블에 표시
                self.ui.MainTable.setItem(self.rowCount, self.word_column,
                                          QTableWidgetItem(current_word.word + current_word.num))
            else:
                self.ui.MainTable.setItem(self.rowCount, self.word_column, QTableWidgetItem(current_word.word))
            if current_word.dict_name != "위키낱말사전" and current_word.dict_name != "Urbandictionary":
                self.URLMap[self.rowCount] = current_word.word_url

            # 발음 버튼
            if len(current_word.pronounces) != 0:
                self.ui.MainTable.setSpan(self.rowCount, self.pos_column, 1, 2)
                self.ui.MainTable.setCellWidget(self.rowCount, self.pos_column, InfoTable(current_word))
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
        if exists(cache_dir):
            shutil.rmtree(cache_dir)

    def change_font(self, lang: str):
        pass
        # try:
        #     if lang == "ko":
        #         self.ui.MainTable.setFont(old_kr_font)
        #         self.ui.queryEdit.setFont(old_kr_query_font)
        #     else:
        #         self.ui.MainTable.setFont(default_font)
        #         self.ui.queryEdit.setFont(query_font)
        # except AttributeError:
        #     self.ui.queryEdit.setFont(old_kr_font)
        #     self.ui.queryEdit.setFont(default_font)

    @staticmethod
    def count_rows_to_add(page: Page):
        count = 0
        for word_count in range(len(page.words)):
            for part_of_speech in page.words[word_count].mean.keys():
                for meanings in range(len(page.words[word_count].mean[part_of_speech])):
                    count += 1
            if len(page.words[word_count].pronounces) != 0 or page.words[word_count].traditional_zh is not None:
                count += 1
        return count

    def load_more(self):
        self.dict_obj.load_next_page()
        self.print_on_table(self.dict_obj.pages[self.page])

    def switch_lang(self, lang: int):
        self.ui.LangBox.setCurrentIndex(lang)
        self.set_focus_on_search()

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
    resources_rc.qInitResources()
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
