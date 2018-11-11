#coding:utf-8

import urllib.request  
from bs4 import BeautifulSoup
import re

#获取城市
def getCity():
    url = 'http://www.ganji.com/index.htm'
    content = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(content,'html.parser',from_encoding='utf-8')
    div = soup.findAll('a')
    div = div[17:-46]
    result = []
    for t in div:
        domin = re.findall('//(.*).ganji',str(t))
        city = re.findall('">(.*)</a>',str(t))
        #print(domin+city)
        result +=(domin+city)
    return result

#获取行业
def getPosition():
    url = 'http://anshan.ganji.com/qiuzhi/'
    content = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(content,'html.parser',from_encoding='utf-8')
    div = soup.findAll('dt')
    div = div[:47]
    result = []
    for t in div:
        domin = re.findall('"/(.*)/"',str(t))
        position = re.findall('_blank">(.*)</a>',str(t))
        #print(domin+position)
        result +=(domin+position)
    return result

#生成域名
city = getCity()
position = getPosition()
finalResult = []
#输出到同一文件夹下的out.txt文件
f = open("out.txt", "w") 
i = 0
for c in city:
    if (i%2)==0:
        j = 0
        for p in position:
            if (j%2)==0:
                temp = "http://"+str(c)+".ganji.com/"+str(p)+"/"
                #temp = "http://"+str(c)+".ganji.com/p0g4"+str(p)+"/"
                print(temp)
                print(temp,file=f)
                finalResult += list(temp)
            j= j+1
    i=i+1
f.close()














