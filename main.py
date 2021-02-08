import requests
import re
import configparser


class Word:
    def __init__(self, word: str, num: int, mean: str, dict_name: str, part_of_speech: str):
        self.word = word                        # 단어
        self.num = num                          # 단어의 번호  ex)사과³
        self.mean = mean                        # 단어의 간략한 뜻
        self.dict_name = dict_name              # 사전 이름 ex) 표준국어대사전
        self.part_of_speech = part_of_speech    # 품사


class DictClient:
    url = None
    res = None
    json_obj = None
    json_itemLength = None
    temp_words = list()
    temp_word_info = None
    cant_show = 0

    def __init__(self, lang: str, query: str, page: int, header: dict, filter_urimalsaem: bool = True):
        # lang: 언어 ex)ko: 한국어, en: 영어, zh: 중국어, ja: 일본어
        # query: 검색어
        # page: json당 15단어가 있음
        # header: user-agent값
        # filter_urimalsaem: 우리말샘 필터링 여부
        self.url = "https://dict.naver.com/api3/" + lang + "ko/search?query=" + query + \
                   "&range=word&page=" + str(page) + "&shouldSearchOpen=false"
        self.res = requests.get(self.url, headers=header)
        self.json_obj = self.res.json()
        regex = re.compile("^(?:<img src=\"https://).*>")
        for k in range(15):
            try:
                word_json = self.json_obj["searchResultMap"]["searchResultListMap"]["WORD"]["items"][k]
                if not regex.match(word_json["expEntry"]):
                    if not(filter_urimalsaem and word_json["sourceDictnameKO"] == "우리말샘"):
                        self.temp_words.append(self.return_word(word_json, k))
                else:
                    self.cant_show = self.cant_show + 1
            except IndexError:
                break

    def return_word(self, raw_word_json, j):
        return Word(raw_word_json["expEntry"].replace("<strong>", "").replace("</strong>", ""),
                    raw_word_json["expEntrySuperscript"],
                    raw_word_json["meansCollector"][0]["means"][0]["value"],  # todo: 여러 의미 불러오기
                    raw_word_json["sourceDictnameKO"],
                    raw_word_json["meansCollector"][0]["partOfSpeech"])  # todo: 여러 의미 품사 불러오기

    def get_words(self):
        return self.temp_words


def lang_to_query():    # 검색할 언어 필터링
    lang = None
    while lang not in ("ko", #"en", "zh", "ja"
                       ):
        lang = input("input language to search\n[ko]한국어 "
                     # "[en]영어 [zh]중국어 [ja]일본어\n>>"
                     )
    return lang


def word_to_query():    # 검색할 값
    word = input("input word to search\n>>")
    return word


def dict_client_loop(times: int):   # times 페이지까지
    for q in range(times):
        return DictClient(LangToQuery, WordToQuery, q + 1, browser_header)


if __name__ == "__main__":
    browser_header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
                                    "Chrome/88.0.4324.150 Safari/537.36"}   # 크롬에서 복사함
    WordList = list()   # 페이지마다 단어 저장
    LangToQuery = lang_to_query()
    WordToQuery = word_to_query()
    dictionary = dict_client_loop(15)
    # noinspection PyUnboundLocalVariable
    WordList = dictionary.get_words()
    for j in range(len(WordList)):
        print(WordList[j].word)
