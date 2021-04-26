import re
import requests
from playsound import playsound
from platform import system
import os
from pathlib import Path
import sys


if system() == "Windows":
    if hasattr(sys, "frozen") and "Program Files" in sys.executable:
        installered = True
        working_dir = str(Path.home()) + "\\AppData\\Roaming\\NaverDict-Client\\"
        cache_dir = working_dir + ".cache\\"
        if not Path.exists(Path(working_dir)):
            Path.mkdir(Path(working_dir))
            if not Path.exists(Path(cache_dir)):
                Path.mkdir(Path(cache_dir))
    else:
        installered = False
        cache_dir = ".cache\\"

browser_header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, "
                                "like Gecko) Chrome/88.0.4324.190 Safari/537.36"}  # 크롬에서 복사함


class Word:
    def __init__(self, lang: str, word: str, num: int, means: dict, dict_name: str, entry_id: str, pronounces: list, traditional_zh = None):
        self.word = word  # 단어
        self.num = num  # 단어의 번호  ex)사과³
        self.mean = means  # {품사 : [뜻, 뜻, 뜻]}
        self.dict_name = dict_name  # 사전 이름 ex)표준국어대사전
        self.entry_id = entry_id  # 단어 상세정보 URL
        self.pronounces = pronounces  # 발음 기호
        self.traditional_zh = traditional_zh  # 중국어
        self.word_url = "https://" + lang + ".dict.naver.com/#/entry/" + lang + "ko/" + self.entry_id
        self.word_json_url = "https://" + lang + ".dict.naver.com/api/platform/" + lang + "ko/entry?entryId=" + self.entry_id
        print(word)

    # def get_traditional_zh(self):
    #     req = requests.get(self.word_json_url, browser_header)
    #     json = req.json()
    #     id_regex = re.compile("<id>\d*</id>")
    #     trsl_pronun_regex = re.compile("</?trsl_pronun>")
    #     try:
    #         id_matching = id_regex.findall(json["entry"]["group"]["entryCommon"]["traditional_entry"])
    #         trsl_pronun_matching = trsl_pronun_regex.findall(json["entry"]["group"]["entryCommon"]["mix_pron"])
    #         try:
    #             traditional_zh = json["entry"]["group"]["entryCommon"]["traditional_entry"].replace(id_matching[0],
    #                                                                                                 "") \
    #                              + " " + json["entry"]["group"]["entryCommon"]["mix_pron"].replace(
    #                 trsl_pronun_matching[0], "").replace(trsl_pronun_matching[1], "")
    #         except IndexError:
    #             try:
    #                 traditional_zh = json["entry"]["group"]["entryCommon"]["mix_pron"].replace(
    #                     trsl_pronun_matching[0], "").replace(trsl_pronun_matching[1], "")
    #             except IndexError:
    #                 traditional_zh = ""
    #     except TypeError:
    #         traditional_zh = ""
    #     finally:
    #         self.traditional_zh = traditional_zh

    def pronounce(self, index: int):
        url = self.pronounces[index][1][1].split("|")[0]
        file_name = cache_dir + url[-32:] + ".mp3"
        if not os.path.exists(file_name):
            req = requests.get(url, browser_header)
            try:
                with open(file_name, "wb") as f:
                    f.write(req.content)
            except FileNotFoundError:
                os.mkdir(cache_dir)
                with open(file_name, "wb") as f:
                    f.write(req.content)
        playsound(file_name)


class Page:
    url = None
    res = None

    def __init__(self, lang: str, query: str, page: int, header: dict):
        self.json_obj = None
        self.words = list()
        self.temp_word_info = None
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
        if len(self.json_obj["searchResultMap"]["searchResultListMap"]["WORD"]["items"]) == 0:
            self.is_page_end = True
            return
        else:
            self.is_page_end = False

        for k in range(15):
            try:
                self.words.append(self.__return_word(
                    self.json_obj["searchResultMap"]["searchResultListMap"]["WORD"]["items"][k]))
                self.words[words_start_index + k] = self.filter_word(self.words[words_start_index + k], self.lang)
            except IndexError:
                if len(self.json_obj["searchResultMap"]["searchResultListMap"]["WORD"]["items"]) == 0:
                    break
        while None in self.words:
            self.words.remove(None)

    def __return_word(self, raw_word_json):

        means_dict = dict()
        for i in range(len(raw_word_json["meansCollector"])):
            means_dict[raw_word_json["meansCollector"][i]["partOfSpeech"]] = list()
            for j in range(len(raw_word_json["meansCollector"][i]["means"])):
                means_dict[raw_word_json["meansCollector"][i]["partOfSpeech"]] \
                    .append(delete_html(raw_word_json["meansCollector"][i]["means"][j]["value"]))

        pronunciations = list()
        for pron in raw_word_json["searchPhoneticSymbolList"]:
            pronunciations.append((pron["phoneticSymbolType"], (pron["phoneticSymbol"], pron["phoneticSymbolPath"])))

        if self.lang == "zh":
            try:
                traditional_zh = raw_word_json["searchTraditionalChineseList"][0]["traditionalChinese"]
            except IndexError:
                traditional_zh = None
        else:
            traditional_zh = None

        word = Word(self.lang, raw_word_json["expEntry"],
                    raw_word_json["expEntrySuperscript"],
                    means_dict,
                    raw_word_json["sourceDictnameKO"],
                    raw_word_json["entryId"],
                    pronunciations, traditional_zh)
        print(" -- :" + word.word)
        return word

    @staticmethod
    def filter_word(word: Word, lang, filter_web_collection: bool = True,
                    filter_urimalsaem: bool = False):
        img_regex = re.compile("<img[^<|>]*>")
        html_regex = re.compile("<[^<|>]*>")
        if filter_web_collection and word.dict_name == "웹수집":
            return None
        if filter_urimalsaem and word.dict_name == "우리말샘":
            return None

        temp_word = word.word
        if lang == "ko":
            old_korean_regex = re.compile("alt=\".*\"")
            img_tags = img_regex.findall(temp_word)
            tags = dict()
            for i in img_tags:
                tags[i] = old_korean_regex.findall(i)[0].replace("alt=", "").replace("\"", "")
            for i in list(tags.keys()):
                temp_word = temp_word.replace(i, tags[i])

        html_list = html_regex.findall(word.word)
        for html in html_list:
            temp_word = temp_word.replace(html, "")
        word.word = temp_word

        for mean_keys_index in list(word.mean.keys()):
            for mean_value_index in range(len(word.mean[mean_keys_index])):
                temp_mean = word.mean[mean_keys_index][mean_value_index]
                if temp_mean is None:
                    return None
                html_list = html_regex.findall(temp_mean)
                for html in html_list:
                    temp_mean = temp_mean.replace(html, "")
                word.mean[mean_keys_index][mean_value_index] = temp_mean

        for mean_keys in word.mean.keys():
            for mean in range(len(word.mean[mean_keys])):
                word.mean[mean_keys][mean] = word.mean[mean_keys][mean].replace("&nbsp;", " ").replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&").replace("&quot;", "\"").replace("&apos;", "'")

        word.num = get_superscript_num(word.num)

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


def delete_html(text: str):
    html_regex = re.compile("<[^<|>]*>")
    html_list = html_regex.findall(text)
    temp_text = text
    for html in html_list:
        temp_text = temp_text.replace(html, "")
    return temp_text