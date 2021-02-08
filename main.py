import requests


class DictClient:
    url = None
    res = None
    json_obj = None

    def __get_url(self, lang, query):
        self.url = "https://dict.naver.com/api3/" + lang + "ko/search?query=" + query + "&range=word"
        return self.url

    def __get_data(self, lang, query, header):
        self.res = requests.get(self.__get_url(lang, query), headers=header)
        return self.res

    def get_and_parse_json(self, lang, query, header):
        self.json_obj = self.__get_data(lang, query, header).json()
        return self.json_obj


def new_dict(list_obj):
    list_obj.append(DictClient())


def lang_to_query():
    lang = None
    while lang not in ("ko", "en", "cn", "jp"):
        lang = input("input language to search\n[ko]한국어 [en]영어 [zh]중국어 [jp]일본어\n>>")
    if lang == "cn":
        lang = "zh"
    elif lang == "jp":
        lang = "ja"
    return lang


def word_to_query():
    word = input("input word to search\n>>")
    return word


if __name__ == "__main__":
    browser_header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
                                    "Chrome/88.0.4324.150 Safari/537.36"}

    clients = list()
    new_dict(clients)
    clients[0].get_and_parse_json(lang_to_query(), word_to_query(), browser_header)
    print(clients[0].json_obj)

