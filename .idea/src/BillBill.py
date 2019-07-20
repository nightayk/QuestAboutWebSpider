import json
import time
import requests
import os
import pymysql


def  getJson(url):
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
    req = requests.get(url, headers=headers)
    gotJson = req.json()
    return gotJson

def timestampTotime(Unixtime):
    time_format = '%Y-%m-%d %H:%M'
    return time.strftime(time_format,time.localtime(Unixtime))

def download(url,vedio_p):
    curPath = os.path.abspath('./Picture/cover_' + vedio_p['title'] + '.jpg')
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
    req = requests.get(url, headers=headers)
    if not os.path.exists(os.path.abspath('./Picture')):
        os.makedirs(os.path.abspath('./Picture'))
    with open(curPath,"wb") as f :
        f.write(req.content)

def getaidData(aid,vedio_p):
    aidData = getJson("https://api.bilibili.com/x/web-interface/archive/stat?aid={}".format(aid))['data']
    vedio_p['coin'] = aidData['coin']
    vedio_p['like'] = aidData['like']
    vedio_p['favorite'] = aidData['favorite']
    vedio_p['reply'] = aidData['reply']
    vedio_p['share'] = aidData['share']


dataList = []

pageNum = 1
vedioNum = 1
vedioNum_max = 50



while(vedioNum <= vedioNum_max):
    spaceData = getJson("https://space.bilibili.com/ajax/member/getSubmitVideos?mid=43536&pagesize=30&tid=0&page={}&keyword=&order=pubdate".format(pageNum))['data']
    videoList = spaceData['vlist']
    vedioPageNum = 0
    while(vedioPageNum < 30 and vedioNum <= vedioNum_max):
        spaceVedioData  = videoList[vedioPageNum]
        print("(B站)正在读取第" + '%d'%vedioNum + "条视频")
        vedio = {
            'id':vedioNum,
            'title':spaceVedioData['title'],
            'subtitle':spaceVedioData['subtitle'],
            'created':timestampTotime(spaceVedioData['created']),
            'description':spaceVedioData['description'].replace('\n',''),
            'length':spaceVedioData['length']
        }
        pic = 'https:' + spaceVedioData['pic']
        download(pic,vedio)
        aid = spaceVedioData['aid']
        getaidData(aid,vedio)
        dataList.append(vedio)
        vedioPageNum = vedioPageNum + 1
        vedioNum = vedioNum + 1
        time.sleep(3)
    pageNum = pageNum + 1

conn = pymysql.connect(host='127.0.0.1',
                       port=3306,
                       user='root',
                       password='root',
                       db='WebSpider',
                       charset='utf8',
                       cursorclass=pymysql.cursors.DictCursor
                       )

cursor = conn.cursor()
sql = 'insert into Bill(id,标题,副标题,发布时间,描述,长度,投币数,点赞数,收藏数,回复数,分享数) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
num = 1;
for vedio in dataList:
    print("(B站)提交数据(" + '%d'%num + "/" + '%d'%vedioNum_max + ")")
    vedioData=(
        vedio['id'],
        vedio['title'],
        vedio['subtitle'],
        vedio['created'],
        vedio['description'],
        vedio['length'],
        vedio['coin'],
        vedio['like'],
        vedio['favorite'],
        vedio['reply'],
        vedio['share']
    )
    cursor.execute(sql,vedioData)
    num = num + 1;
conn.commit();
cursor.close()
conn.close()
print("(B站)数据已全部提交至数据库")
