# 웹 크롤링 동작
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import time

from datetime import datetime
from bs4 import BeautifulSoup


webdriver_manager_directory = ChromeDriverManager().install()
browser = webdriver.Chrome(service=ChromeService(webdriver_manager_directory))
# ChromeDriver 실행
from selenium.common.exceptions import NoSuchElementException, NoSuchWindowException    # Element : 웹요소 찾지 못할 때 / Window : 창이 없거나 찾을 수 없을 때
# Chrome WebDriver의 capabilities 속성 사용
capabilities = browser.capabilities
from selenium.webdriver.common.by import By
# - 정보 획득
# from selenium.webdriver.support.ui import Select      # Select : dropdown 메뉴 다루는 클래스
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# 몽고db 저장
from pymongo import MongoClient
# mongodb에 접속
mongoClient = MongoClient("mongodb://localhost:27017")
# database 연결
database = mongoClient["steam"]
# collection 작업
tos = database['tos']
# - 주소 입력

browser.get("https://steamcommunity.com/app/2178420/reviews/?browsefilter=mostrecent&snr=1_5_100010_&p=1&filterLanguage=all")
time.sleep(1)

lang = browser.find_element(by=By.CSS_SELECTOR, value='#language_pulldown').click()
time.sleep(1)

lang_ko = browser.find_element(by=By.CSS_SELECTOR, value='#language_dropdown > div > a:nth-child(4)').click()
time.sleep(5)


# 스크롤 끝까지 내리기
element_body = browser.find_element(by=By.CSS_SELECTOR,value='body')
previous_scrollHeight = 0
while True:
    element_body.send_keys(Keys.END)
    current_scrollHeight = browser.execute_script('return document.body.scrollHeight')
    if previous_scrollHeight >= current_scrollHeight:
        break
    else:
        previous_scrollHeight = current_scrollHeight
    time.sleep(2)


# 전체 페이지
contents_bundle = browser.find_elements(by=By.CSS_SELECTOR, value='#AppHubCards > div')


for content in contents_bundle:

    # page 내 한줄 당 세분화 카드
    page_contents = content.find_elements(by=By.CSS_SELECTOR, value='#AppHubCards > div > div')
    
    for incontent in page_contents:

        # 세분화 카드 내 요소 추출
        incontents = incontent.find_elements(by=By.CSS_SELECTOR, value='#AppHubCards > div > div > div')

        for text in incontents:

            # 도움 추천 텍스트 추출
            try:
                ishelpful = text.find_element(by=By.CSS_SELECTOR, value='div.apphub_CardContentMain > div.apphub_UserReviewCardContent > div').text
            except:
                ishelpful = ''

            # 추천 / 비추천
            try:
                isrecommend = text.find_element(by=By.CSS_SELECTOR, value='div.apphub_CardContentMain > div.apphub_UserReviewCardContent > div.vote_header > div.reviewInfo > div.title').text
            except:
                isrecommend = ''

            # 플레이 시간
            try:
                playtime = text.find_element(by=By.CSS_SELECTOR, value='div.apphub_CardContentMain > div.apphub_UserReviewCardContent > div.vote_header > div.reviewInfo > div.hours').text
            except:
                playtime = ''

            # 세부 내용
            try:
                contents = text.find_element(by=By.CSS_SELECTOR, value='div.apphub_CardContentMain > div.apphub_UserReviewCardContent > div.apphub_CardTextContent').text
                contents_list = contents.split('\n')
                
                # 게시 날짜
                date = contents_list[0].split(' ')
                date = ' '.join(date[2:])
                # 내용
                content_text = ''
                for i in contents_list[1:]:
                    if i[-1] not in ['.','"',"'",'?','!']:
                        content_text += i
                        content_text += '.'
                        content_text += ' '
                    else:
                        if i != contents_list[-1]:
                            content_text += i
                            content_text += ' '
                        else:
                            content_text += i
            except:
                continue
            
            # 작성인
            try:
                user = text.find_element(by=By.CSS_SELECTOR, value='div.apphub_CardContentAuthorBlock.tall > div.apphub_friend_block_container > div > div > a:nth-child(2)').text
                pass
            except:
                user = ''
                pass

            # 데이터 저장
            data={
            'ishelpful' : ishelpful,
            'isrecommend' : isrecommend,
            'playtime' : playtime,
            'date' : date,
            'content_text' : content_text,
            'user' : user
            }
            tos.insert_one(data)

browser.close()
