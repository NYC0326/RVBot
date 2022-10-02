import tweepy
import pymysql
import time
from selenium import webdriver

def connect_api():
    # 트위터 Application에서 발급 받은 key 정보들 문자열로 입력
    bearer_token = "AAAAAAAAAAAAAAAAAAAAAIMjSQEAAAAA6gT%2B0g0rQaFyyvq8d9AxGWDUOJA%3Dc4oVoZQVto44d3keuDNayrYFvoQfFPBjM0wiEMDPuTdRW5o6wB"
    consumer_key = "J5B04Nh8JpE8FrdJntuuiCQGI"
    consumer_secret = "cxQg0D4RvCRLfrpu5DEDuEKxUzfBKKGX3B5T71OLs6t3Ri1jRU"
    access_token = "806164211986415617-NDuMDJjcTeTzva4dxaAq2tj056czdmL"
    access_token_secret = "lWgRvZ6VxVyNr4pSi0AE9WC7mEIZpTdsmUI12i0e4sZll"

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)

    return api

def UserTimelineCursor(api, screen_name, num):
    tweets = tweepy.Cursor(api.user_timeline, screen_name=screen_name, tweet_mode="extended").items(num)
    return tweets

def checkUpdate():
    # API에 연결하여 최근 10개 트윗(답글 포함) 가져오기
    api = connect_api()
    RV_timeline = UserTimelineCursor(api, '@RVsmtown', 10)

    id_db, id_crawl = [], []
    for RV_tweet in RV_timeline:
        id_crawl.append(RV_tweet.id_str)

    sql = 'SELECT * FROM tweets limit 10;'
    cursor.execute(sql)
    result = cursor.fetchall()
    for dictionary in result:
        id_db.append(dictionary['id'])

    update = [i for i in id_crawl if i not in id_db]
    now = time.strftime('%H:%M')
    if (update == []):
        print("업데이트 없음")
    else:
        print("[%s] 레드벨벳 트위터 업데이트" % now)
        updatedTweets = len(update)
        RV_timeline = UserTimelineCursor(api, '@RVsmtown', updatedTweets)
        for RV_tweet in RV_timeline:
            sql = "INSERT INTO tweets VALUES('" + RV_tweet.id_str + "');"
            cursor.execute(sql)
            db.commit()

def DCupload(content, title, address=None):
    # 제목 입력
    driver.find_element_by_id('subject').send_keys(title)
    # 말머리 선택 / 현재 선택된 갤러리는 말머리가 없음
    #driver.find_element_by_xpath("//li[@data-no='0']").click()
    # HTML으로 쓰기 방식 변경
    driver.find_element_by_xpath('//*[@id="chk_html"]').click()
    # time.sleep(1)
    #driver.switch_to.frame(driver.find_element_by_xpath("//iframe[@name='tx_canvas_wysiwyg']"))
    # 본문 입력
    driver.find_element_by_xpath('//*[@id="chk_html"]').click()
    driver.find_element_by_tag_name("body").send_keys(content)
    driver.find_element_by_xpath('//*[@id="chk_html"]').click()
    # 이미지 업로드 창 선택
    if address != None:
        driver.find_element_by_xpath('//*[@id="tx_image"]/a').click();
        time.sleep(1)
        # 이미지 업로드 창으로 변경
        driver.switch_to.window(driver.window_handles[-1])
        driver.find_element_by_css_selector("input[type='file']").send_keys(address)
        time.sleep(5)
        driver.find_element_by_xpath("//button[@class='btn_apply']").click()
        time.sleep(1.5)
        # 글쓰기 폼으로 진입
        driver.switch_to.window(driver.window_handles[0])
    # 글쓰기 저장
    driver.switch_to.default_content()
    driver.find_element_by_xpath('//*[@id="chk_html"]').click()
    driver.find_element_by_xpath("//button[@class='btn_blue btn_svc write']").click()
    # 저장 딜레이
    time.sleep(1)
    # 다시 갤사이트로 가기
    driver.get(gallpath)
    time.sleep(1)


db = pymysql.connect(
    user='s19026',
    passwd='1111',
    host = 'dev.gsa.hs.kr',
    db = 's19026',
    port = 18001,
    charset = 'utf8'
)

cursor = db.cursor(pymysql.cursors.DictCursor)

gallpath = 'https://gall.dcinside.com/mgallery/board/write/?id=redvelvet_vlive'
transparency = False

# 크롬 환경 변수
options = webdriver.ChromeOptions()
# 크롬 투명하게 실행
if transparency is True:
    options.add_argument('headless')
# 크롬 창 1300*800으로 실행 (하는 이유는 화면 창 사이즈에 따라서 웹 구조가 조금 달라질 수도 있어서)
options.add_argument('--window-size=1300,800')
# 크롬 드라이버 로드
driver = webdriver.Chrome('chromedriver_win32/chromedriver.exe', options=options)
driver.implicitly_wait(1)
driver.get('https://www.dcinside.com/') # 디시인사이드 로그인 페이지 로드
driver.find_element_by_name('user_id').send_keys('rvchartbot') # 아이디
driver.find_element_by_name('pw').send_keys('dkfmaekdnsrkdtks123') # 패스워드
driver.find_element_by_id('login_ok').click() # 로그인
driver.get(gallpath) # 글을 쓰고자 하는 갤러리로 이동

checkUpdate()