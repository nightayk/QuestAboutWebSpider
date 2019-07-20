# -*- coding: UTF-8 -*-
import urllib
import urllib.request
import re
import pymysql
import time



def getHtml(url):
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
    req = urllib.request.Request(url=url, headers=headers)
    currentHtml = urllib.request.urlopen(req).read().decode('utf-8')
    return currentHtml


REG_MOVIE = re.compile(r'<li>(.*?)</li>',re.DOTALL)
REG_TITLE = re.compile(r'<span class="title">(.*?)</span>',re.DOTALL)
REG_RETITLE = re.compile(r'<span class="title">&nbsp;/&nbsp;([\u4e00-\u9fa5·]*?)</span>',re.DOTALL)
REG_OTHERNAME = re.compile(r'<span class="other">(.*?)</span>',re.DOTALL)
REG_HKNAME = re.compile(r'([^;/]*?)\(港\)',re.DOTALL)
REG_TWNAME = re.compile(r'([^;/]*?)\(台\)',re.DOTALL)
REG_HKTWNAME = re.compile(r'([^;/]*?)\(港/台\)',re.DOTALL)
REG_ISPLAYABLE = re.compile(r'<span class="playable">\[(.*?)\]</span>',re.DOTALL)
REG_INFOPAGE = re.compile(r'<a href="(.*?)">',re.DOTALL)
REG_DIRECTOR = re.compile(r'rel="v:directedBy">(.*?)</a>',re.DOTALL)
REG_MAINACTOR = re.compile(r'rel="v:starring">([\u4e00-\u9fa5·]*?)</a',re.DOTALL)
REG_YEAR = re.compile(r'<div class="bd">(.*?)&nbsp;/&nbsp;',re.DOTALL)
REG_AREAandTYPE = re.compile(r'<div class="bd">(.*?)</p>',re.DOTALL)
REG_AREA = re.compile(r'&nbsp;/&nbsp;(.*?)&nbsp;/&nbsp;',re.DOTALL)
REG_TYPE = re.compile(r'&nbsp;/&nbsp;.*?&nbsp;/&nbsp;(.*?)\n',re.DOTALL)
REG_SCORE = re.compile(r'<span class="rating_num" property="v:average">(.*?)</span>',re.DOTALL)
REG_EVALUATORS = re.compile(r'<span>(.*?)评价</span>',re.DOTALL)
REG_QUOTE = re.compile(r'<span class="inq">(.*?)</span>',re.DOTALL)
REG_NEXTPAGE = re.compile(r'<link rel="next" href="(.*?)"/>',re.DOTALL)

def getMovie(currentHtml,REG):
    movieList = REG.findall(currentHtml)
    del movieList[0]
    return movieList

def getTitlename(movie,REG,REG_RE,CNList,FEList):
    titleList = REG.findall(movie)
    CNList.append(titleList[0])
    if len(titleList)==2 :
        judge = REG_RE.findall(movie)
        if judge :
            FEList.append("无")
        else :
            FEList.append(titleList[1][13:].replace("&#39;","'"))
    else :
        FEList.append("无");

def getOthername(movie,OTHER_REG,HKTW_REG,HK_REG,TW_REG,HKList,TWList):
    getOther = OTHER_REG.findall(movie)
    toRead = getOther[0].replace(" ","")
    HKTW = HKTW_REG.findall(toRead)
    if HKTW :
        HKList.append(HKTW[0])
        TWList.append(HKTW[0])
    else :
        HK = HK_REG.findall(toRead)
        if HK :
            HKList.append(HK[0])
        else :
            HKList.append("无")
        TW = TW_REG.findall(toRead)
        if TW :
            TWList.append(TW[0])
        else :
            TWList.append("无")

def getIsPlayable(movie,REG,List):
    section = REG.findall(movie)
    if section :
        List.append(section[0])
    else :
        List.append("不可播放")

def getInfoPage(movie,REG):
    InfoPage = REG.findall(movie)
    return InfoPage[0]

def getSomething(html,REG,List):
    section = REG.findall(html)
    if section :
        List.append(section[0])
    else :
        List.append("无")

def getMainActor(html,REG,List):
    section = REG.findall(html)
    if section :
        collection = ""
        num = len(section)
        i = 0
        while(i < num-1):
            collection = collection + section[i] + "/"
            i = i + 1
        collection = collection + section[num-1]
        List.append(collection)
    else :
        List.append("无")

def getYear(movie,REG,List):
    section = REG.findall(movie)
    List.append(section[0][-4:])

def getAreaandType(movie,REG,REG_A,REG_T,List_A,List_T):
    section = REG.findall(movie)
    getSomething(section[0],REG_A,List_A)#获取电影地区
    getSomething(section[0],REG_T,List_T)#获取电影类型

def getNextPage(html,REG):#获取下一页的url地址
    section = REG.findall(html)
    if section :
        nextUrl = 'https://movie.douban.com/top250' + section[0].replace("amp;","")
    else :
        nextUrl = ""
    return nextUrl

CNnameList = []
FEnameList = []
HKnameList = []
TWnameList = []
PlayableList = []
DirectorList = []
MainActorList = []
YearList = []
AreaList = []
TypeList = []
ScoreList = []
EvaluatorsList = []
QuoteList = []

nextPage = 'https://movie.douban.com/top250'
pageNum = 0
while(nextPage != ""):
    pageNum = pageNum + 1
    print("(豆瓣)正在读取第" + '%d'%pageNum + "页的数据...")
    pageHtml = getHtml(nextPage)
    currentMovie = getMovie(pageHtml,REG_MOVIE)
    for oneMovie in currentMovie:
        time.sleep(1)
        getTitlename(oneMovie,REG_TITLE,REG_RETITLE,CNnameList,FEnameList)
        getOthername(oneMovie,REG_OTHERNAME,REG_HKTWNAME,REG_HKNAME,REG_TWNAME,HKnameList,TWnameList)
        getIsPlayable(oneMovie,REG_ISPLAYABLE,PlayableList)
        InfoPageHtml = getHtml(getInfoPage(oneMovie,REG_INFOPAGE))
        getMainActor(InfoPageHtml,REG_MAINACTOR,MainActorList)
        getYear(oneMovie,REG_YEAR,YearList)
        getAreaandType(oneMovie,REG_AREAandTYPE,REG_AREA,REG_TYPE,AreaList,TypeList)
        getSomething(InfoPageHtml,REG_DIRECTOR,DirectorList)#获取导演名称
        getSomething(oneMovie,REG_SCORE,ScoreList)#获取电影评分
        getSomething(oneMovie,REG_EVALUATORS,EvaluatorsList)#获取评分人数
        getSomething(oneMovie,REG_QUOTE,QuoteList)#获取电影评语
    nextPage = getNextPage(pageHtml,REG_NEXTPAGE)
print("读取完毕")

conn = pymysql.connect(host='127.0.0.1',
                       port=3306,
                       user='root',
                       password='root',
                       db='WebSpider',
                       charset='utf8',
                       cursorclass=pymysql.cursors.DictCursor
                       )

cursor = conn.cursor()
sql = 'insert into DoubanFilms(id,中文名,外文名,港译名,台译名,是否可播放,导演,主演,上映年份,国家地区,类型,评分,评价人数,电影评语) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
num = 0
last = len(CNnameList)
while(num < last):
    data = (
            num+1,
            CNnameList[num],
            FEnameList[num],
            HKnameList[num],
            TWnameList[num],
            PlayableList[num],
            DirectorList[num],
            MainActorList[num],
            YearList[num],
            AreaList[num],
            TypeList[num],
            ScoreList[num],
            EvaluatorsList[num],
            QuoteList[num]
         )
    cursor.execute(sql,data)
    num = num + 1
    print("(豆瓣)提交数据(" + '%d'%num + "/" + '%d'%last + ")")
conn.commit()
cursor.close()
conn.close()
print("(豆瓣)数据已全部提交至数据库")