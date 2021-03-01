import re
import requests

browser_header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, "
                                "like Gecko) Chrome/88.0.4324.190 Safari/537.36"}  # 크롬에서 복사함


class Word:
    def __init__(self, lang: str, word: str, num: int, means: dict, dict_name: str, entry_id: str, pronounce: str):
        self.lang = lang
        self.word = word  # 단어
        self.num = num  # 단어의 번호  ex)사과³
        self.mean = means  # {품사 : [뜻, 뜻, 뜻]}
        self.dict_name = dict_name  # 사전 이름 ex)표준국어대사전
        self.word_url = entry_id  # 단어 상세정보 URL
        self.pronounce = pronounce  # 발음 기호
        self.traditional_zh = None  # 중국어

    def get_traditional_zh(self):
        req = requests.get(self.word_url, browser_header)
        json = req.json()
        id_regex = re.compile("<id>\d*</id>")
        trsl_pronun_regex = re.compile("</?trsl_pronun>")
        try:
            id_matching = id_regex.findall(json["entry"]["group"]["entryCommon"]["traditional_entry"])
            trsl_pronun_matching = trsl_pronun_regex.findall(json["entry"]["group"]["entryCommon"]["mix_pron"])
            try:
                traditional_zh = json["entry"]["group"]["entryCommon"]["traditional_entry"].replace(id_matching[0],
                                                                                                    "") \
                                 + " " + json["entry"]["group"]["entryCommon"]["mix_pron"].replace(
                    trsl_pronun_matching[0], "").replace(trsl_pronun_matching[1], "")
            except IndexError:
                try:
                    traditional_zh = json["entry"]["group"]["entryCommon"]["mix_pron"].replace(
                        trsl_pronun_matching[0], "").replace(trsl_pronun_matching[1], "")
                except IndexError:
                    traditional_zh = ""
        except TypeError:
            traditional_zh = ""
        finally:
            self.traditional_zh = traditional_zh


class Page:
    url = None
    res = None
    def __init__(self, lang: str, query: str, page: int, header: dict):
        self.json_obj = None
        self.words = list()
        self.temp_word_info = None
        self.is_page_end = False
        self.lang = None
        self.query = None
        self.page = int()
        self.page = page
        self.lang = lang
        self.query = query
        # lang: 언어 ex)ko: 한국어, en: 영어, zh: 중국어, ja: 일본어
        # query: 검색어
        # page: json 당 15단어가 있음
        # header: user-agent 값
        self.url = "https://dict.naver.com/api3/" + lang + "ko/search?query=" + query + \
                   "&range=word&page=" + str(self.page) + "&shouldSearchOpen=false"
        self.res = requests.get(self.url, headers=header)
        self.json_obj = self.res.json()
        words_start_index = len(self.words)
        for k in range(15):
            try:
                self.words.append(self.__return_word(
                    self.json_obj["searchResultMap"]["searchResultListMap"]["WORD"]["items"][k]))
                self.words[words_start_index + k] = self.filter_word(self.words[words_start_index + k])
            except IndexError:
                if len(self.json_obj["searchResultMap"]["searchResultListMap"]["WORD"]["items"]) == 0:
                    self.is_page_end = True
                    break
        while None in self.words:
            self.words.remove(None)

    def __return_word(self, raw_word_json):
        means_dict = dict()
        for i in range(len(raw_word_json["meansCollector"])):
            means_dict[raw_word_json["meansCollector"][i]["partOfSpeech"]] = list()
            for j in range(len(raw_word_json["meansCollector"][i]["means"])):
                means_dict[raw_word_json["meansCollector"][i]["partOfSpeech"]] \
                    .append(raw_word_json["meansCollector"][i]["means"][j]["value"])

        dest_link = "https://" + self.lang + ".dict.naver.com/api/platform/" + self.lang + "ko/entry.nhn?entryId=" + \
                    raw_word_json["entryId"]

        return Word(self.lang, raw_word_json["expEntry"],
                    raw_word_json["expEntrySuperscript"],
                    means_dict,
                    raw_word_json["sourceDictnameKO"],
                    dest_link,
                    raw_word_json)

    @staticmethod
    def filter_word(word: Word, filter_web_collection: bool = True,
                    filter_urimalsaem: bool = False):
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

        word.num = get_superscript_num(word.num)

        if word.lang == "zh":
            word.get_traditional_zh()

        return word


class Dictionary:
    def __init__(self):
        self.pages = list()
        self.lang = None
        self.query = None

    def set_query(self, lang: str, query: str):
        self.lang = lang
        self.query = query

    def load_next_page(self):
        self.pages.append(Page(self.lang, self.query, len(self.pages) + 1, browser_header))

    def load_first_page(self, lang: str, query: str):
        self.set_query(lang, query)
        self.load_next_page()


def get_superscript_num(num: int or None):
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
