'''

'''

from bs4 import BeautifulSoup
import requests
import random
import json
import time
def getHtmlContent(url):
    header_choices = [
        "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/537.75.14",
        "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)",
        'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
        'Opera/9.25 (Windows NT 5.1; U; en)',
        'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
        'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
        'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
        'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9',
        "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Ubuntu/11.04 Chromium/16.0.912.77 Chrome/16.0.912.77 Safari/535.7",
        "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:10.0) Gecko/20100101 Firefox/10.0 "
    ]
    headvalue = dict()
    headvalue['User-Agent'] = random.choice(header_choices)
    r = requests.get(url, headers=headvalue)
    try:
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except:
        return str()

def extractHouseInfoLink(searchResult):
    search1 = searchResult.find(class_='sellListContent')
    itemLink = search1.find_all(class_='title')  # 同样采用css定位的原理
    pureLink = list()
    for l in itemLink:
        temp = l.find('a')
        pureLink.append(temp.get('href'))
    return pureLink

def extractHouseInfo(htmlContent):
    # 利用词典保存结果
    InfoResult = dict()
    house_detail = BeautifulSoup(htmlContent,features="lxml")
    #获取价格信息
    price_info = house_detail.find(class_='price')
    InfoResult['总价'] = price_info.find(class_='total').text
    InfoResult['总价单位'] = price_info.find(class_='unit').text
    InfoResult['单价'] = price_info.find(class_='unitPriceValue').next_element
    InfoResult['单价单位'] = price_info.find(class_='unitPriceValue').next_element.next_element.next_element
    houseInfo = house_detail.find(class_='houseInfo')
    InfoResult['房屋年代'] = houseInfo.find(class_='area').find(class_='subInfo').text
    aroundInfo = house_detail.find(class_='aroundInfo')
    InfoResult['小区名称'] = aroundInfo.find(class_='communityName').find(class_='info').text
    InfoResult['所在区域'] = aroundInfo.find(class_='areaName').find(class_='info').text
    introContent = house_detail.find(class_='introContent')
    infoList = introContent.find(class_='content').find_all('li')

    for item in infoList:
        key=item.next_element.next_element
        if '房屋户型'==key:
            InfoResult['户型'] = item.next_element.next_element.next_element
        elif '所在楼层'==key:
            InfoResult['楼层'] = item.next_element.next_element.next_element
        elif '建筑面积'==key:
            InfoResult['建筑面积'] = item.next_element.next_element.next_element
        elif '房屋朝向'==key:
            InfoResult['房屋朝向'] = item.next_element.next_element.next_element
        elif '装修情况'==key:
            InfoResult['装修情况'] = item.next_element.next_element.next_element
        elif '梯户比例'==key:
            InfoResult['梯户比例'] = item.next_element.next_element.next_element
        elif '配备电梯'==key:
            InfoResult['配备电梯']=item.next_element.next_element.next_element
        elif '产权年限'==key:
            InfoResult['产权年限'] = item.next_element.next_element.next_element

    return InfoResult

def getNextPage(searchResult):
    pagebox = searchResult.find(class_='page-box house-lst-page-box')
    pagedata = pagebox.get('page-data')
    pagedata = json.loads(pagedata)
    curPage = pagedata['curPage']
    totalPage = pagedata['totalPage']
    if curPage!=totalPage:
        templateUrl = pagebox.get('page-url')
        newUrl = templateUrl.format(page=curPage+1)
        return newUrl
    else:
        return None

if __name__=='__main__':
    startUrl = 'https://su.lianjia.com/ershoufang/xiangcheng/?\
    sug=%E7%9B%B8%E5%9F%8Ehttps://su.lianjia.com/ershoufang\
    /xiangcheng/?sug=%E7%9B%B8%E5%9F%8E'  # 苏州相城区二手房搜索页第一页

    baseUrl = 'https://su.lianjia.com'
    resultList=list()
    resultF=open('housePrice_suzhou_xiangcheng.csv','w+')
    title=['index','小区名称','所在区域','总价','总价单位','单价','单价单位'
           ,'房屋年代','户型','楼层','建筑面积','房屋朝向','装修情况','梯户比例'
           ,'配备电梯','产权年限']
    for t in title:
        if t=='产权年限':
            resultF.write(t)
        else:
            resultF.write(t+',')
#    resultF.write(title)

    resultF.write('\n')
    cnt=0
    scrapCnt=0
    tipsTemp = '已经爬取记录：{cnt1} 条;已经串行化存储记录：{cnt2} 条'

    while 1:
        searchResult=getHtmlContent(startUrl)
        if searchResult:
            resultTag=BeautifulSoup(searchResult,features="lxml")
            linkList=extractHouseInfoLink(resultTag)
            for link in linkList:
                time.sleep(1)
                houseContent=getHtmlContent(link)
                if houseContent:
                    houseInfo=extractHouseInfo(houseContent)
                    resultList.append(houseInfo)
                    scrapCnt=scrapCnt+1
                    print('\r'+tipsTemp.format(cnt1=scrapCnt,cnt2=cnt),end='')
                    if len(resultList)==100:
                        #串行化至文件
                        for info in resultList:
                            resultF.write(str(cnt))
                            cnt=cnt+1
                            for k in title[1:]:
                                resultF.write(',')
                                if k in info:
                                    resultF.write(info[k])
                                else:
                                    resultF.write(' ')
                            resultF.write('\n')
                        resultF.flush()
                        resultList.clear()
            nextResult=getNextPage(resultTag)
            if nextResult==None:
                break
            else:
                startUrl=baseUrl+nextResult
        else:
            break

    if len(resultList)>0:
        # 串行化至文件
        for info in resultList:
            resultF.write(str(cnt))
            cnt = cnt + 1
            for k in title[1:]:
                resultF.write(' ')
                if k in info:
                    resultF.write(info[k])
                else:
                    resultF.write(' ')
            resultF.write('\n')

        resultF.flush()
        resultList.clear()
        print('\r' + tipsTemp.format(cnt1=scrapCnt, cnt2=cnt), end='')
    resultF.close()







