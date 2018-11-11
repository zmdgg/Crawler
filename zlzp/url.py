#coding:utf-8

import urllib.request  
from bs4 import BeautifulSoup
import re

#获取赶集网城市名
def getGanjiCity():
    url = 'http://www.ganji.com/index.htm'
    content = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(content,'html.parser',from_encoding='utf-8')
    div = soup.findAll('a')
    div = div[17:-46]
    result = []
    for t in div:
        city = re.findall('">(.*)</a>',str(t))
        result +=city
    return result

#获取智联招聘城市，并根据赶集网筛选出主要城市350个
def getCity(ganji):
    url = 'http://jobs.zhaopin.com/citymap.html'
    content = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(content,'html.parser',from_encoding='utf-8')
    div = soup.findAll('a')
    count = 0
    result=[]
    #f = open('city.txt','a+')
    for t in div:
        domin = re.findall('"http://jobs.zhaopin.com/(.*)/">',str(t))
        city = re.findall('">(.*)</a>',str(t))
        #print(str(city)[2:-2])
        for i in ganji:
            #print(i)
            if i==str(city)[2:-2]:
                #temp =str(domin)[2:-2]
                result += domin
                #print(temp)
                count = count+1
                break
                #f.write(temp+"\n")
    #print(count)
    #f.close()
    return result

#获取行业
def getPosition():
    url = 'http://jobs.zhaopin.com/aba/'
    content = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(content,'html.parser',from_encoding='utf-8')
    div = soup.findAll('div',attrs={'id':'search_dom2'})
    #div = div[:47]
    result = []
    for t in div:
        domin = re.findall('aba/(.*)/"',str(t))
        result += domin
        #print(domin)
    return result

#生成域名
ganji = getGanjiCity()
city = getCity(ganji)
position = getPosition()
#输出到同一文件夹下的out.txt文件
f = open("out.txt", "w") 
for c in city:
    for p in position:
        temp = "http://jobs.zhaopin.com/"+str(c)+"/"+str(p)+"/"
        #print(temp)
        print(temp,file=f)
f.close()














