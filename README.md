# NaverDict-Client는 간단한 네이버 사전 클라이언트입니다.

![Naver Dictionary Client_mainScreen](https://user-images.githubusercontent.com/61839345/107855805-e8b82080-6e67-11eb-9bd0-1fca21e0650f.gif)
1. 드롭다운 리스트로 검색할 언어를 선택하십시오. 
2. 검색할 단어를 입력한 후 엔터 키를 누르거나 검색 버튼을 누르십시오.
3. 더 많은 단어들을 불러오려면, 더 불러오기 버튼을 누르십시오.
* Ctrl + 1|2|3|4로 언어 전환을 할 수 있습니다.
  - 1: 국어, 2: 영어, 3: 중국어, 4: 일본어
* Ctrl + Q로 커서를 검색창에 놓을 수 있습니다.
-----
* *압축을 해제한 후, 폴더 루트의 NaverDict-Client.exe를 실행하세요.*
* *실행 파일이 디지털 서명되지 않아 Windows Defender 경고가 뜨니 추가 정보를 눌러 실행하세요.*
* 직접 실행하려면

      git clone https://github.com/Jeong-Jingyo/NaverDict-Client.git
      cd NaverDict-Client
      python3 -m venv venv
      #윈도우
      ./venv/bin/activate
      #우분투
      source ./venv/bin/activate
      pip3 install -r requirements.txt
      python3 src/main.py
      
* PyQt5 프레임워크를 사용하였습니다.
