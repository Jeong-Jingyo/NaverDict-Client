import requests
from mainUI import Ui_MainWindow
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QTableWidget, QShortcut
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QKeySequence, QFont
import re

langFamily = ["ko", "en", "zh", "ja"]


class Word:
    def __init__(self, word: str, num: int, means: dict, dict_name: str, entry_id: str):
        self.word = word  # 단어
        self.num = num  # 단어의 번호  ex)사과³
        self.mean = means  # {품사 : [뜻, 뜻, 뜻]}
        self.dict_name = dict_name  # 사전 이름 ex)표준국어대사전
        self.word_url = entry_id
        self.traditional_zh = None


class Dictionary:
    url = None
    res = None
    json_obj = None
    words = list()
    temp_word_info = None
    is_page_end = False
    lang = None
    query = None

    def get_word(self, lang: str, query: str, page: int, header: dict):
        self.lang = lang
        self.query = query
        # lang: 언어 ex)ko: 한국어, en: 영어, zh: 중국어, ja: 일본어
        # query: 검색어
        # page: json 당 15단어가 있음
        # header: user-agent 값
        word_start_index = len(self.words)
        self.url = "https://dict.naver.com/api3/" + lang + "ko/search?query=" + query + \
                   "&range=word&page=" + str(page) + "&shouldSearchOpen=false"
        self.res = requests.get(self.url, headers=header)
        self.json_obj = self.res.json()
        for k in range(15):
            try:
                self.words.append(
                    self.__return_word(self.json_obj["searchResultMap"]["searchResultListMap"]["WORD"]["items"][k]))
            except IndexError:
                if len(self.json_obj["searchResultMap"]["searchResultListMap"]["WORD"]["items"]) == 0:
                    self.is_page_end = True
                    break
        word_end_index = len(self.words)
        return word_start_index, word_end_index

    def __return_word(self, raw_word_json):
        means_dict = dict()
        for i in range(len(raw_word_json["meansCollector"])):
            means_dict[raw_word_json["meansCollector"][i]["partOfSpeech"]] = list()
            for j in range(len(raw_word_json["meansCollector"][i]["means"])):
                means_dict[raw_word_json["meansCollector"][i]["partOfSpeech"]] \
                    .append(raw_word_json["meansCollector"][i]["means"][j]["value"])

        dest_link = "https://" + self.lang + ".dict.naver.com/api/platform/" + self.lang + "ko/entry.nhn?entryId=" + \
                    raw_word_json["entryId"]

        return Word(raw_word_json["expEntry"],
                    raw_word_json["expEntrySuperscript"],
                    means_dict,
                    raw_word_json["sourceDictnameKO"],
                    dest_link)

    @staticmethod
    def filter_word(word: Word, filter_web_collection: bool = True, filter_urimalsaem: bool = False) -> Word or None:
        img_regex = re.compile("<img.*>")
        html_regex = re.compile("<[^<|>]*>")
        if filter_web_collection and word.dict_name == "웹수집":
            return None
        if filter_urimalsaem and word.dict_name == "우리말샘":
            return None
        if bool(img_regex.match(word.word)):
            return None

        temp_word = word.word
        html_list = html_regex.findall(word.word)
        for html in html_list:
            temp_word = temp_word.replace(html, "")
        word.word = temp_word

        for mean_keys_index in list(word.mean.keys()):
            for mean_value_index in range(len(word.mean[mean_keys_index])):
                temp_mean = word.mean[mean_keys_index][mean_value_index]
                html_list = html_regex.findall(temp_mean)
                for html in html_list:
                    temp_mean = temp_mean.replace(html, "")
                word.mean[mean_keys_index][mean_value_index] = temp_mean

        word.num = upper_num_to_unicode(word.num)

        return word


def upper_num_to_unicode(num: int or None):
    upper_nums = [u"⁰", u"¹", u"²", u"³", u"⁴", u"⁵", u"⁶", u"⁷", u"⁸", u"⁹"]

    temp_upper_chars = []
    temp_uppers = ""
    if num is not None:
        for temp_num_char in str(num):
            temp_upper_chars.append(upper_nums[int(temp_num_char)])
        for j in temp_upper_chars:
            temp_uppers = temp_uppers + j
        return temp_uppers
    else:
        return None


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

        query_key.activated.connect(lambda: self.ui.queryEdit.setFocus())
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
                self.dict_obj.words[i].traditional_zh = self.get_traditional_zh(self.dict_obj.words[i].word_url)

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

    @staticmethod
    def get_traditional_zh(url: str):
        req = requests.get(url, browser_header)
        print(req.text)
        json = req.json()
        id_regex = re.compile("<id>\d*</id>")
        trsl_pronun_regex = re.compile("</?trsl_pronun>")
        try:
            id_matching = id_regex.findall(json["entry"]["group"]["entryCommon"]["traditional_entry"])
            trsl_pronun_matching = trsl_pronun_regex.findall(json["entry"]["group"]["entryCommon"]["mix_pron"])
            try:
                traditional_zh = json["entry"]["group"]["entryCommon"]["traditional_entry"].replace(id_matching[0], "")\
                                 + " " + json["entry"]["group"]["entryCommon"]["mix_pron"].replace(trsl_pronun_matching[0], "").replace(trsl_pronun_matching[1], "")
                return traditional_zh
            except IndexError:
                try:
                    traditional_zh = json["entry"]["group"]["entryCommon"]["mix_pron"].replace(trsl_pronun_matching[0], "").replace(trsl_pronun_matching[1], "")
                    return traditional_zh
                except IndexError:
                    return ""
        except TypeError:
            return ""

    def switch_lang(self, lang: int):
        self.ui.LangBox.setCurrentIndex(lang)


if __name__ == '__main__':
    browser_header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
                                    "Chrome/88.0.4324.150 Safari/537.36"}  # 크롬에서 복사함
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
