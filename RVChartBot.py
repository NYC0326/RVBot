#-*- coding:utf-8 -*
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from matplotlib import pyplot as plt
from matplotlib import rc
from matplotlib.pyplot import figure
from PIL import Image
import requests, time, threading, os, json, urllib.request
import matplotlib as mpl

# 그래프 띄울 필요가 없고 그냥 저장만 하면 되서 사용
mpl.use('Agg')

# plt.rcParams.update({'figure.max_open_warning': 0})
# max_open_warning 경고 안뜨게 할려고 적어둔 거였는데
# 그냥 plt.close() 하면 안뜬다는 말이 있어서 테스트 해보게 주석처리함

header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko'}

fivepath = r'C:\Users\남유찬\PycharmProjects\RVChartBot\five.png'
dailypath = r'C:\Users\남유찬\PycharmProjects\RVChartBot\daily.png'
gallpath = r'https://gall.dcinside.com/mgallery/board/write/?id=redvelvetreveluv'
# gallpath = r'https://gall.dcinside.com/mgallery/board/write/?id=redvelvet_reality'
rvNames = ['레드벨벳', 'IRENE', 'SEULGI', 'WENDY', 'JOY', 'YERI']
transparency = True

#멜론에 관한 데이터를 얻는 클래스
class MelonData:
    def __init__(self):
        self.year = None
        self.month = None
        self.date = None
        self.timenow = None
        self.data = None
        self.datalen = None

    # 오늘 날짜 크롤링 (datetime 쓰기 귀찮아서)
    def getDate(self):
        req = requests.get('https://www.melon.com/chart/index.htm', headers=header)
        html = req.text
        soup = BeautifulSoup(html, 'html.parser')
        today = soup.find("span", {"class": "year"}).text
        self.year = today[:4]
        self.month = today[5:7]
        self.date = today[8:10]
        return self.year, self.month, self.date

    # 현재 멜론 XX시 차트 크롤링
    def time(self):
        req = requests.get('https://www.melon.com/chart/index.htm', headers=header)
        html = req.text
        soup = BeautifulSoup(html, 'html.parser')
        self.timenow = soup.find("span", {"class": "hour"}).text
        return self.timenow

    # 멜론 5분 실수치 크롤링 // 0이면 수치만, 1이면 이름까지
    def getFiveData(self, param):
        try:
            MelonChartURL = 'https://m.app.melon.com/chart/hourly/fiveChartGraph.json?cpId=AS40&cpKey=14LNC3&v=4.0'
            MelonChartPage = urllib.request.urlopen(MelonChartURL)
            MelonChartData = json.loads(MelonChartPage.read())
            self.data = []
            self.name = []
            for i in range(len(MelonChartData['response']['GRAPHDATALIST'])):
                fiveS = []
                self.name.append(MelonChartData['response']['GRAPHDATALIST'][i]['GRAPHCHARTINFO']['SONGNAME'])
                for j in range(len(MelonChartData['response']['GRAPHDATALIST'][i]['GRAPHDATA'])):
                    fiveS.append(MelonChartData['response']['GRAPHDATALIST'][i]['GRAPHDATA'][j]['VAL'])
                del fiveS[0]
                for j in range(len(fiveS)):
                    fiveS[j] = float(fiveS[j])
                self.data.append(fiveS)
            if param == 0:
                return len(self.data[0])
            if param == 1:
                return self.data
            if param == 2:
                return self.data, self.name
        except:
            if param == 0:
                return 100
            if param == 1:
                return 100
            if param == 2:
                return 100, 100

    def getDailyData(self, param):
        try:
            MelonChartURL = 'https://m2.melon.com/chart/hourly/hourlyChartGraph.json?appVer=5.0.4&cpId=IS40&cpKey=17LNM9&resolution=2&v=4.0'
            MelonChartPage = urllib.request.urlopen(MelonChartURL)
            MelonChartData = json.loads(MelonChartPage.read())
            if param == 'time':
                return MelonChartData['response']['XCATE']
            self.data = []
            self.SID = []
            self.name = []
            for i in range(len(MelonChartData['response']['GRAPHDATALIST'])):
                self.SID.append(MelonChartData['response']['GRAPHDATALIST'][i]['SONGID'])
                top3D = []
                for j in range(len(MelonChartData['response']['GRAPHDATALIST'][i]['GRAPHDATA'])):
                    top3D.append(MelonChartData['response']['GRAPHDATALIST'][i]['GRAPHDATA'][j]['VAL'])
                for k in range(len(top3D)):
                    if top3D[k] == "":
                        top3D[k] = 0.00
                    top3D[k] = float(top3D[k])
                self.data.append(top3D)
            for i in range(len(self.SID)):
                req = requests.get('https://www.melon.com/song/detail.htm?songId=' + self.SID[i], headers=header)
                html = req.text
                soup = BeautifulSoup(html, "html.parser")
                self.name.append(soup.find("div", {"class": "song_name"}).text.replace('곡명', '').strip())
            return self.data, self.SID, self.name
        except:
            return 100, 100, 100

#플로에 관한 데이터를 얻는 클래스
class floData:
    def __init__(self):
        self.timenow = None
    def time(self):
        flochartURL = "https://api.music-flo.com/display/v1/browser/chart/1"
        flochartPage = urllib.request.urlopen(flochartURL)
        flochartData = json.loads(flochartPage.read())
        self.timenow = flochartData["data"]["chart"]["basedOnUpdate"][:2]+':00'
        return self.timenow

#벅스에 대한 데이터를 얻는 클래스
class bugsData:
    def __init__(self):
        self.timenow = None
    def time(self):
        req = requests.get('https://music.bugs.co.kr/chart', headers=header)
        html = req.text
        soup_b = BeautifulSoup(html, 'html.parser')
        self.timenow = soup_b.time.em.text
        return self.timenow

timeOrigMelon = MelonData().time()
timeOrigMelon2 = MelonData().time()    #시간이 바뀌었는지 비교하기 위해서 처음 시간을 저장해 놓은 전역 변수
'''
멜론에는 5분마다 그 곡의 점유율(전체 들은 곡중 그 곡을 들은 비율)을 업데이트 해주는데 만약 새로운 값이 나왔다면
데이터의 길이가 달라졌을 것 이므로, 처음 길이를 저장해 놓은 전역 변수
'''
fiveOrigLength = MelonData().getFiveData(0)
floTimeOrig = floData().time()   # 플로차트의 시간 (ex) 18:00 차트)
timeOrigBugs = bugsData().time() # 벅스차트의 시간 (ex) 18:00 차트)

# 크롬 환경 변수
options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-logging"])
# 크롬 투명하게 실행
if transparency is True:
    options.add_argument('headless')
# 크롬 창 1920*1080으로 실행 (하는 이유는 화면 창 사이즈에 따라서 웹 구조가 조금 달라질 수도 있어서)
options.add_argument('--window-size=1920,1080')
# 크롬 드라이버 로드
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.implicitly_wait(5)
driver.get('https://www.dcinside.com/') # 디시인사이드 로그인 페이지 로드
driver.find_element(By.NAME, 'user_id').send_keys('rvchartbot') # 아이디
driver.find_element(By.NAME, 'pw').send_keys('dkfmaekdnsrkdtks123') # 패스워드
driver.find_element(By.ID, 'login_ok').click() # 로그인
driver.get(gallpath) # 글을 쓰고자 하는 갤러리로 이동

# 10 미만의 시간단위에 앞에 0을 붙혀주는 함수 ex. 8시 1분 -> 08시 01분
def numToString(n):
    if n < 10:
        n = '0' + str(n)
    return n;

# 함수 이름 처럼 데이터들이 업데이트 됐는지 확인하는 함수 (5초마다 크롤링해서 업데이트를 확인한다)
def checkUpdate():
    # 최초 환경 값 불러오기
    global header
    global timeOrigMelon
    global timeOrigMelon2
    global timeOrigBugs
    global floTimeOrig
    global fiveOrigLength
    # 음원 차트 시간 값 불러오기
    try:
        timeNowMelon = MelonData().time()
        timeBugs = bugsData().time()
        flochartTime = floData().time()
    except:
        print('음원 차트 시간 불러오기 실패')
    if fiveOrigLength != 100:    
        # 멜론 5분 실수치 퍼오기
        try:
            fiveSeries = MelonData().getFiveData(1)
        except:
            print('멜론 5분 실수치 불러오기 실패')
    
        #실시간 차트 업데이트
        try:
            if timeOrigMelon != timeNowMelon:
                timeOrigMelon = timeNowMelon
                print('멜론 실시간 차트 업데이트')
                melon_daily()
        except:
            pass
        
        # 정각이 지난 한 10~30초 정도 아무 데이터가 없을 때가 있다. 그때를 위한 코드이다.
        if fiveOrigLength == 0:
            try:
                fiveSeries = MelonData().getFiveData(1)
            except:
                pass
            
        # 만약 5분 차트가 업데이트 되었다면, 5분 차트 그래프를 그려주는 함수를 실행한다.
        try:
            if fiveOrigLength != len(fiveSeries[0]):
                if len(fiveSeries[0]) != 1:
                    fiveOrigLength = len(fiveSeries[0])
                    print('5분 차트 업데이트')
                    melon_five()
        except:
            pass

    # 만약 실시간 차트 (1시간 기준)가 업데이트 되었다면, 실시간 차트를 그려주는 함수를 실행한다.
    try:
        if floTimeOrig != flochartTime and timeNowMelon != timeOrigMelon2 and timeBugs != timeOrigBugs:
            floTimeOrig = flochartTime
            timeOrigMelon2 = timeNowMelon
            timeOrigBugs = timeNowMelon
            print('레드벨벳 실시간 순위')
            RV_rank()
    except:
        pass
    threading.Timer(5, checkUpdate).start()

# 팬들이 모여있는 디씨인사이드 사이트의 갤러리에 현재 음원 순위, 차트 그래프 사진을 업로드 하는 함수이다.
def DCupload(content, title, address=None):
    # 제목 입력
    driver.find_element(By.ID, 'subject').send_keys(title)
    # 말머리 선택 / 현재 선택된 갤러리는 말머리가 없음
    driver.find_element(By.XPATH, "//li[@data-no='0']").click()
    # HTML으로 쓰기 방식 변경
    driver.find_element(By.XPATH, '//*[@id="chk_html"]').click()
    # time.sleep(1)
    # HTML로 쓰기 방식 변경하면 알아서 글쓰는 공간으로 옮겨짐
    # driver.switch_to.frame(driver.find_element_by_xpath("//iframe[@name='tx_canvas_wysiwyg']"))
    # 본문 입력
    driver.find_element(By.TAG_NAME, "body").send_keys(content)
    driver.find_element(By.XPATH, '//*[@id="chk_html"]').click()
    # 이미지 업로드 창 선택
    if address != None:
        driver.find_element(By.XPATH, '//*[@id="tx_image"]/a').click();
        time.sleep(1)
        # 이미지 업로드 창으로 변경
        driver.switch_to.window(driver.window_handles[-1])
        driver.find_element(By.CSS_SELECTOR, "input[type='file']").send_keys(address)
        time.sleep(5)
        driver.find_element(By.XPATH, "//button[@class='btn_apply']").click()
        time.sleep(1.5)
        # 글쓰기 폼으로 진입
        driver.switch_to.window(driver.window_handles[0])
    # 글쓰기 저장
    driver.switch_to.default_content()
    driver.find_element(By.XPATH, '//*[@id="chk_html"]').click()
    driver.find_element(By.XPATH, "//button[@class='btn_blue btn_svc write']").click()
    # 저장 딜레이
    driver.implicitly_wait(1)
    # 다시 갤사이트로 가기
    driver.get(gallpath)
    driver.implicitly_wait(1)

# 멜론 5분 실수치를 이용하여 그래프를 만들어 주는 함수이다.
def melon_five():
    fiveSeries, fiveName = MelonData().getFiveData(2) # 5분 실수치와 5분 차트 노래 제목들을 퍼온다.
    fiveSeriesFormat = [[format(i, ".2f") for i in fiveSeries[j]] for j in range(len(fiveSeries))]
    fivexaxis = list(range(0, 5*len(fiveSeries[0]), 5)) # x축을 5분, 10분, 15분 이렇게 5분 간격으로 만들어준다.
    figure(figsize=(10.5, 6.5))  # 그래프 크기
    g_max = max(fiveSeries[0])  # 5분 실수치 최대값
    for i in range(1, len(fiveSeries)):
        if g_max < max(fiveSeries[i]):  # 하위 순위의 곡에서 최대 실수치가 있으면 실수치 최대값 변경
            g_max = max(fiveSeries[i])
    rc('font', family='BM JUA_TTF')
    plt.rcParams['axes.facecolor'] = 'dimgray' # 그래프 배경 색
    plt.rcParams['savefig.facecolor'] = 'lightskyblue' # 그래프 바깥쪽 색
    linecolor = ['dodgerblue', 'darkorange', 'limegreen', 'orchid', 'goldenrod', 'tomato', 'mediumturquoise']  # 선색깔
    for i in range(len(fiveSeriesFormat)):
        if (len(fiveSeriesFormat[i]) != 0) and (len(fiveSeriesFormat[i]) == len(fiveSeriesFormat[0])):  # 선 그리기
            plt.plot(fivexaxis, fiveSeries[i], c=linecolor[i], lw='3.5', label=fiveName[i])
    plt.rcParams["legend.facecolor"] = 'whitesmoke'
    leg = plt.legend(fiveName, loc=1)  # 오른쪽 상단에 있는 주석에 들어가는 노래제목, 위치 지정
    for txtxt in leg.get_texts():
        plt.setp(txtxt, color='black')  # 주석 텍스트 색깔 지정
    plt.grid(True)
    plt.xlim(0, 60)  # x축 값 제한
    plt.ylim(0, g_max + 1)  # y축 값은 최대 실수치보다 크게 지정
    textcolor = ['cyan', 'orange', 'lightgreen', 'violet', 'gold', 'coral', 'turquoise']  # 실수치 텍스트 색깔 지정
    for i in range(len(fiveSeriesFormat)):
        if (len(fiveSeriesFormat[i]) != 0 and len(fiveSeriesFormat[i]) == len(fiveSeriesFormat[0])):
            mpl.rcParams['text.color'] = textcolor[i]
            texts = []
            for x, y, s in zip(fivexaxis, fiveSeries[i], fiveSeriesFormat[i]):
                texts.append(plt.text(x, y, s, fontsize=15))
    # 오늘 날짜 가져오기
    mday = numToString(time.localtime().tm_mday)
    # 시간도 날짜와 마찬가지
    hour = numToString(time.localtime().tm_hour);
    # 분도 날짜와 마찬가지
    minute = numToString(int((time.localtime().tm_min) / 5) * 5)
    plt.title('[2021년 ' + str(time.localtime().tm_mon) + '월 ' + str(mday) + '일 ' + str(hour) + ':' + str(minute) + ']' + ' 멜론 5분 차트 by RVBot', color='black')  # 그래프 제목
    plt.subplots_adjust(left=0.05, bottom=0.05, right=0.95, top=0.95, hspace=0, wspace=0)  # 그래프 위치 조절

    plt.savefig('five.png', dpi=300)  # 그래프 저장
    plt.close()
    fivegraph = Image.open('five.png')  # 그래프 저장 위치 지정
    reveluv = Image.open('reveluv.png')  # 갤러리 낙관 위치 지정
    summermagic = Image.open('summermagic.png')  # 개인 낙관 위치 지정
    fivegraph.paste(reveluv, (2494, 1371), reveluv)  # 갤러리 낙관 박을 위치 지정 후 합치기
    # fivegraph.paste(summermagic, (2094,1461), summermagic)    #개인 낙관 박을 위치 지정
    fivegraph.save('five.png')  # 그래프 저장하기
    #fivegraph.show()  # 그래프 보여주기
    title = '[%s:%s] 멜론 5분 차트' % (hour, minute)
    content = str()
    for i in range(len(fiveSeries)):
        n = len(fiveSeries[0])
        content = content + "[%s시 %d위] %s (%.3f) <br>" % (str(hour), i+1, fiveName[i], (fiveSeries[i][n-1]-fiveSeries[i][n-2]))
        for j in range(len(fiveSeries[i])):
            content = content + "%.3f || " % fiveSeries[i][j]
        content = content + "<br><br>"
        if i+1 != len(fiveSeries):
            content = content + "[%.3f]<br><br>" % (fiveSeries[i][n-1] - fiveSeries[i+1][n-1])
    check = 0
    for i in range(len(fiveSeries)):
        # 이 코드는 특정 가수의 곡이 1, 2, 3등 안에 있을 때 글을 올리게끔 하는 코드이다. 여기선 레드벨벳을 예시로 적어놨다.
        if fiveName[i] in rvNames: #레드벨벳의 최근 곡이 1, 2, 3위에 있는지 확인하는 조건문
            print('[%s:%s] 레드벨벳 노래가 있으므로 글 올림' % (hour, minute))
            #DCupload(content, title, fivepath) # 글을 올려주는 함수 호출
            print(content)
            break
        else:
            check+=1
            if check == 2:
                print('[%s:%s] 레드벨벳 노래가 없으므로 글을 올리지 않음' % (hour, minute))

# 위에 멜론 5분 차트 그래프 그려주는 함수와 같이 이건 실시간 차트를 그래프로 그려주는 함수이다.
# 위 함수와 코드가 동일하므로 세세한 주석은 생략했습니다.
def melon_daily():
    top3Data, top3SID, top3Name = MelonData().getDailyData('')
    xcate = MelonData().getDailyData('time')
    top3DataFormat = [[format(i, ".2f") for i in top3Data[j]] for j in range(len(top3Data))]
    top3xaxis = xcate.split(',')
    #fig = plt.figure()
    figure(figsize=(10.5, 6.5))  # 그래프 크기
    if os.path.exists('daily.png'):
        os.remove('daily.png')
    g_max = max(top3Data[0])  # 5분 실수치 최대값 선언
    for i in range(1, len(top3Data)):
        if g_max < max(top3Data[i]):  # 하위 순위의 곡에서 최대 실수치가 있으면 그걸로 바꿈
            g_max = max(top3Data[i])
    rc('font', family='BM JUA_TTF')
    plt.rcParams['axes.facecolor'] = 'dimgray'
    plt.rcParams['savefig.facecolor'] = 'lightskyblue'
    linecolor = ['dodgerblue', 'darkorange', 'limegreen', 'orchid', 'goldenrod', 'tomato', 'mediumturquoise']  # 선색깔
    for i in range(len(top3Data)):
        if (len(top3Data[i]) != 0) and (len(top3Data[i]) == len(top3Data[0])):  # 선 그림
            plt.plot(top3xaxis, top3Data[i], c=linecolor[i], lw='3.5', label=top3Name[i])
    plt.rcParams["legend.facecolor"] = 'whitesmoke'
    leg = plt.legend(top3Name, loc=1)  # 오른쪽 상단에 있는 주석에 들어가는 노래제목, 위치 지정
    for txtxt in leg.get_texts():
        plt.setp(txtxt, color='black')  # 주석 텍스트 색깔 지정
    plt.grid(True)
    plt.xlim(0, 18)  # x축 값 제한
    plt.ylim(0, g_max + 0.5)  # y축 값은 최대 실수치보다 크게 지정
    textcolor = ['cyan', 'orange', 'lightgreen', 'violet', 'gold', 'coral', 'turquoise']  # 실수치 텍스트 색깔 지정
    darktextcolor = ['darkcyan', 'darkgoldenrod', 'darkgreen', 'magenta', 'goldenrod', 'tomato', 'mediumturquoise']
    for i in range(len(top3Data)):
        if (len(top3Data[i]) != 0 and len(top3Data[i]) == len(top3Data[0])):
            mpl.rcParams['text.color'] = textcolor[i]
            texts = []
            for x, y, s in zip(top3xaxis, top3Data[i], top3DataFormat[i]):
                if s == '0.00':
                    pass
                else:
                    plt.text(x, y, s, fontsize=15)
            texts2 = []
            mpl.rcParams['text.color'] = darktextcolor[i]
            texts2.append(plt.text(18, top3Data[i][18], format(top3Data[i][18], ".2f"), fontsize=15))
    mday = numToString(time.localtime().tm_mday)
    hour = numToString(time.localtime().tm_hour)
    plt.title('[2021년 ' + str(time.localtime().tm_mon) + '월 ' + str(mday) + '일 ' + str(hour) + ':' + '00]' + ' 멜론 실시간 차트 by RVBot', color='black')  # 그래프 제목
    plt.subplots_adjust(left=0.05, bottom=0.05, right=0.95, top=0.95, hspace=0, wspace=0)  # 그래프 위치 조절
    plt.savefig('daily.png', dpi=300)  # 그래프 저장
    plt.close()
    dailygraph = Image.open('daily.png')  # 그래프 저장 위치 지정
    reveluv = Image.open('reveluv.png')  # 갤러리 낙관 위치 지정
    summermagic = Image.open('summermagic.png')  # 개인 낙관 위치 지정
    dailygraph.paste(reveluv, (2494, 1351), reveluv)  # 갤러리 낙관 박을 위치 지정
    # fivegraph.paste(summermagic, (2094,1461), summermagic)    #개인 낙관 박을 위치 지정
    dailygraph.save('daily.png')  # 그래프 저장하기
    dailygraph.show()  # 그래프 보여주기
    title = '[%s:00] 멜론 실시간 차트' % hour
    content=str()
    for i in range(len(top3Name)):
        n = len(top3Data[0])
        content = content + "[%d위] %s (%.3f) <br>" % (i + 1, top3Name[i], (top3Data[i][n - 1] - top3Data[i][n - 2]))
        for j in range(len(top3Data[i])):
            content = content + "%.3f || " % top3Data[i][j]
        content = content + "<br><br>"
        if i+1 != len(top3Data):
            content = content + "[%.3f]<br><br>" % (top3Data[i][n-1] - top3Data[i+1][n-1])
    check = 0
    for i in range(len(top3Name)):
        if top3Name[i] in rvNames:
            print('[%s:00] 레드벨벳 노래가 있으므로 글 올림' % (hour))
            #DCupload(content, title, dailypath)
            break
        else:
            check += 1
            if check==2:
                print('[%s:%s] 레드벨벳 노래가 없으므로 글을 올리지 않음' % (hour, minute))

# 이 함수는 흔히 사용하는 4대 음원 사이트 (멜론, 지니, 벅스, 플로)에서 특정 가수의 곡들이 몇위를 하고 있고, 증감 폭을
# 구해주는 함수로, 이 또한 텍스트로 변환하여 글을 올리는 함수를 호출하여 글을 올릴 수 있다.
def RV_rank():
#                  레드벨벳 멜론 차트 등수 크롤링
    global header
    MelonChartURL = 'https://m2.melon.com/chart/hourly/hourlyChartList.json?cpId=IS40&cpKey=17LNM9&isRecom=Y&pageSize=100&resolution=2&startIndex=1&v=4.0'
    MelonChartPage = urllib.request.urlopen(MelonChartURL)
    MelonChartData = json.loads(MelonChartPage.read())
    SongName = []
    CurRank = []
    RankGap = []
    RankType = []
    ArtistName = []
    string_m = '<br>' + '-' * 21 + '<font color="#00CC33"><멜론 실시간 순위></font>' + '-' * 21 + '<br>'
    for i in range(len(MelonChartData['response']['CHARTLIST'])):
        SongName.append(MelonChartData['response']['CHARTLIST'][i]['SONGNAME'])
        CurRank.append(MelonChartData['response']['CHARTLIST'][i]['CURRANK'])
        RankGap.append(MelonChartData['response']['CHARTLIST'][i]['RANKGAP'])
        RankType.append(MelonChartData['response']['CHARTLIST'][i]['RANKTYPE'])
        Artist = []
        for j in range(len(MelonChartData['response']['CHARTLIST'][i]['ARTISTLIST'])):
            Artist.append(MelonChartData['response']['CHARTLIST'][i]['ARTISTLIST'][j]['ARTISTNAME'])
        ArtistName.append(Artist)
    for i in range(len(RankType)):
        if RankType[i] == 'NONE':
            RankType[i] = '<font color="black">-</font>'
        if RankType[i] == 'UP':
            RankType[i] = '<font color="red">' + RankGap[i] + '↑ </font>'
        if RankType[i] == 'DOWN':
            RankType[i] = '<font color="blue">' + RankGap[i] + '↓ </font>'
        if RankType[i] == 'NEW':
            RankType[i] = '<font color="green">' + 'NEW' + '</font>'

    for i in range(100):
        for j in range(len(rvNames)):
            for k in range(len(ArtistName[i])):
                if rvNames[j] in ArtistName[i][k]:
                    string_m = string_m + '{:<5}'.format(str(i + 1) + '위') + '</font>' + RankType[i] + '<font color="purple"> ' + '{:<30}'.format(SongName[i].lstrip()) + '</font><br>'
            if rvNames[j] in SongName[i]:
                string_m = string_m + '{:<5}'.format(str(i + 1) + '위') + '</font>' + RankType[i] + '<font color="purple"> ' + '{:<30}'.format(SongName[i].lstrip()) + '</font><br>'
    ##                  레드벨벳 멜론 실시간 차트 등수 크롤링

    ##                  레드벨벳 멜론 24H 차트 등수 크롤링


    req_m = requests.get('https://www.melon.com/chart/index.htm', headers=header)
    html_m = req_m.text
    soup = BeautifulSoup(html_m, 'html.parser')
    title_m = soup.find_all("div", {"class": "ellipsis rank01"})
    artist_m = soup.find_all("div", {"class": "ellipsis rank02"})
    for i in range(len(title_m)):
        title_m[i], artist_m[i] = title_m[i].text, artist_m[i].text
    string_m2 = '' + '-' * 20 + '<font color="#00CC33"><멜론 TOP 100 순위></font>' + '-' * 20 + '<br>'
    for j in range(100):
        for i in range(len(rvNames)):
            if rvNames[i] in artist_m[j]:
                string_m2 = string_m2 + '{:<5}'.format(str(j + 1) + '위') + '</font>' + '<font color="purple"> ' + '{:<30}'.format(title_m[j].strip()) + '</font><br>'
            if rvNames[i] in title_m[j]:
                string_m2 = string_m2 + '{:<5}'.format(str(j + 1) + '위') + '</font>' + '<font color="purple"> ' + '{:<30}'.format(title_m[j].strip()) + '</font><br>'
    ##                  레드벨벳 지니 차트 등수 크롤링
    title_g = []
    artist_g = []
    fluct_g = []
    string_g = '        <br>'+'-'* 25 + '<font color="#21B5E6"><지니 순위></font>'+'-'*25+'<br>'

    for i in range(1, 6):
        req_g = requests.get('https://www.genie.co.kr/chart/top200?pg=' + str(i), headers=header)
        html_g = req_g.text
        soup = BeautifulSoup(html_g, 'html.parser')

        titles_g = soup.find_all("td", {"class": "info"})
        artists_g = soup.find_all("td", {"class": "info"})
        flucts_g = soup.find_all("span", {"class": "rank"})

        for t in titles_g:
            title_g.append(t.find('a', {"class": "title ellipsis"}).text)

        for a in artists_g:
            artist_g.append(a.find('a', {"class": "artist ellipsis"}).text)

        for f in flucts_g:
            fluct_g.append(f.find('span').text)

    for i in reversed(range(525)):
        if (i % 105 == 0 or i % 105 == 1 or i % 105 == 2 or i % 105 == 3 or i % 105 == 4):
            del fluct_g[i]

    fluct_g = fluct_g[0::2]

    for i in range(250):
        if fluct_g[i] == '유지':
            fluct_g[i] = '<font color="black">-</font>'
        if fluct_g[i][len(fluct_g[i]) - 2] == '상':
            fluct_g[i] = fluct_g[i].replace("상승", "")
            fluct_g[i] = '<font color="red">' + fluct_g[i] + '↑ </font>'
        if fluct_g[i][len(fluct_g[i]) - 2] == '하':
            fluct_g[i] = fluct_g[i].replace("하강", "")
            fluct_g[i] = '<font color="blue">' + fluct_g[i] + '↓ </font>'
        if fluct_g[i] == 'new':
            fluct_g[i] = '<font color="green">' + 'NEW' + '</font>'

    for j in range(250):
        for i in range(len(rvNames)):
            if rvNames[i] in artist_g[j]:
                string_g = string_g + '{:<5}'.format(str(j + 1) + '위') + '</font>' + '{:<5}'.format(fluct_g[j]) + '<font color="purple"> ' + '{:<30}'.format(title_g[j].lstrip()) + '</font><br>'
            if rvNames[i] in title_g[j]:
                string_g = string_g + '{:<5}'.format(str(j + 1) + '위') + '</font>' + '{:<5}'.format(fluct_g[j]) + '<font color="purple"> ' + '{:<30}'.format(title_g[j].lstrip()) + '</font><br>'
    ##                  레드벨벳 지니 차트 등수 크롤링

    ##                  레드벨벳 벅스 차트 등수 크롤링
    req_b = requests.get('https://music.bugs.co.kr/chart', headers=header)
    html_b = req_b.text
    soup = BeautifulSoup(html_b, 'html.parser')

    titles_b = soup.find_all("p", {"class": "title"})
    artists_b = soup.find_all("p", {"class": "artist"})
    flucts_b = soup.find_all("p", {"class": "change"})

    title_b = []
    fluct_b = []
    fluct_b2 = []
    string_b = '        <br>'+'-'*25+'<font color="#F94232"><벅스 순위></font>'+'-'*25+'<br>'

    for t in titles_b:
        title_b.append(t.find('a').text)

    for f in flucts_b:
        fluct_b.append(f.find('em').text)
        fluct_b2.append(f.find_all('span'))

    for i in range(100):
        if str(fluct_b[i]) == '0':
            fluct_b[i] = '<font color="black">-</font>'
        else:
            if str(fluct_b2[i]) == '[<span class="arrow"></span>, <span>계단 상승</span>]':
                fluct_b[i] = '<font color="red">' + fluct_b[i] + '↑ </font>'
            if str(fluct_b2[i]) == '[<span class="arrow"></span>, <span>계단 하락</span>]':
                fluct_b[i] = '<font color="blue">' + fluct_b[i] + '↓ </font>'

    for j in range(100):
        for i in range(len(rvNames)):
            if rvNames[i] in str(artists_b[j]):
                string_b = string_b + '{:<5}'.format(str(j + 1) + '위') + '</font>' + fluct_b[j] + ' <font color="purple"> ' + '{:<30}'.format(title_b[j]) + '</font><br>'
            if rvNames[i] in str(titles_b[j]):
                string_b = string_b + '{:<5}'.format(str(j + 1) + '위') + '</font>' + fluct_b[j] + ' <font color="purple"> ' + '{:<30}'.format(title_b[j]) + '</font><br>'
    ##                  레드벨벳 벅스 차트 등수 크롤링

    ##                  레드벨벳 플로 차트 등수 크롤링
    flochartURL = "https://api.music-flo.com/display/v1/browser/chart/1"
    flochartPage = urllib.request.urlopen(flochartURL)
    flochartData = json.loads(flochartPage.read())
    string_f = '        <br>' + '-' * 25 + '<font color="#3f3fff"><플로 순위></font>' + '-' * 25 + '<br>'
    title_f = list()
    artist_f = list()
    fluct_f = list()
    for i in range(len(flochartData["data"]["chart"]["trackList"])):
        artists_f = []
        title_f.append(flochartData["data"]["chart"]["trackList"][i]["name"])
        fluct_f.append(str(flochartData["data"]["chart"]["trackList"][i]["rank"]["rankBadge"]))
        for j in range(len(flochartData["data"]["chart"]["trackList"][i]["artistList"])):
            artists_f.append(flochartData["data"]["chart"]["trackList"][i]["artistList"][j]["name"])
        artist_f.append(artists_f)

    for i in range(100):
        if int(fluct_f[i]) == 0:
            fluct_f[i] = '<font color="black">-</font>'
        elif int(fluct_f[i]) > 0:
            fluct_f[i] = '<font color="red">' + str(fluct_f[i]) + '↑ </font>'
        elif int(fluct_f[i]) < 0:
            fluct_f[i] = '<font color="blue">' + str(abs(int(fluct_f[i]))) + '↓ </font>'

    for i in range(100):
        for j in range(len(rvNames)):
            if len(artist_f[i]) == 1:
                if rvNames[j] in artist_f[i][0]:
                    string_f = string_f + '{:<5}'.format(str(i + 1) + '위') + '</font>' + fluct_f[i] + '<font color="purple"> ' + '{:<30}'.format(title_f[i].lstrip()) + '</font><br>'
                if rvNames[j] in title_f[i]:
                    string_f = string_f + '{:<5}'.format(str(i + 1) + '위') + '</font>' + fluct_f[i] + '<font color="purple"> ' + '{:<30}'.format(title_f[i].lstrip()) + '</font><br>'

            else:
                for k in range(len(artist_f[i])):
                    if rvNames[j] in artist_f[i][k]:
                        string_f = string_f + '{:<5}'.format(str(i + 1) + '위') + '</font>' + fluct_f[i] + '<font color="purple"> ' + '{:<30}'.format(title_f[i].lstrip()) + '</font><br>'
                    if rvNames[j] in title_f[i]:
                        string_f = string_f + '{:<5}'.format(str(i + 1) + '위') + '</font>' + fluct_f[i] + '<font color="purple"> ' + '{:<30}'.format(title_f[i].lstrip()) + '</font><br>'

    ##                  레드벨벳 플로 차트 등수 크롤링
    content = string_m + string_m2 + string_g + string_b + string_f
    hour = time.localtime().tm_hour
    if hour < 10:
        hour = str('0' + str(time.localtime().tm_hour))
    title = '[%s:00] 레드벨벳 음원 순위' % hour
    DCupload(title=title, content=content)

# 처음 시작 하기 위해선 업데이트를 확인하는 함수를 불러온다.
checkUpdate()
