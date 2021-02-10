import requests
import re
import configparser


class Word:

    def __init__(self, word: str, num: int, means: dict, dict_name: str):
        self.word = word                        # 단어
        self.num = num                          # 단어의 번호  ex)사과³
        self.mean = means                       # {품사 : [뜻, 뜻, 뜻]}
        self.dict_name = dict_name              # 사전 이름 ex)표준국어대사전



class Dictionary:
    url = None
    res = None
    json_obj = None
    words = list()
    temp_word_info = None
    is_page_end = False

    def get_word(self, lang: str, query: str, page: int, header: dict):
        # lang: 언어 ex)ko: 한국어, en: 영어, zh: 중국어, ja: 일본어
        # query: 검색어
        # page: json당 15단어가 있음
        # header: user-agent값
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

    @staticmethod
    def __return_word(raw_word_json):
        means_dict = dict()
        for i in range(len(raw_word_json["meansCollector"])):
            means_dict[raw_word_json["meansCollector"][i]["partOfSpeech"]] = list()
            for j in range(len(raw_word_json["meansCollector"][i]["means"])):
                means_dict[raw_word_json["meansCollector"][i]["partOfSpeech"]]\
                    .append(raw_word_json["meansCollector"][i]["means"][j]["value"])

        return Word(raw_word_json["expEntry"],
                    raw_word_json["expEntrySuperscript"],
                    means_dict,
                    raw_word_json["sourceDictnameKO"])

    def filter_word(self, filter_web_collection: bool = True, filter_urimalsaem: bool = False):
        for i in range(len(self.words)):
            if filter_web_collection and self.words[i].dict_name == "웹수집":
                self.words[i] = None
            if filter_urimalsaem and self.words[i].dict_name == "우리말샘":
                self.words[i] = None
        while None in self.words:
            self.words.remove(None)
        return self.words


def lang_to_query():    # 검색할 언어
    lang = None
    while lang not in ("ko", "en", "zh", "ja"):
        lang = input("input language to search\n[ko]한국어 [en]영어 [zh]중국어 [ja]일본어\n>>")
    return lang


def word_to_query():    # 검색할 값
    word = input("input word to search\n>>")
    return word


if __name__ == "__main__":
    browser_header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
                                    "Chrome/88.0.4324.150 Safari/537.36"}   # 크롬에서 복사함
    LangToQuery = lang_to_query()
    WordToQuery = word_to_query()

    WordDict = Dictionary()
    for i in range(15):
        WordDict.get_word(LangToQuery, WordToQuery, i + 1, browser_header)
        if WordDict.is_page_end:
            break
    WordDict.filter_word()
