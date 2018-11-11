#coding:utf-8
from urllib import request
import requests
from bs4 import BeautifulSoup
import re
import pymysql

import urllib.error
import datetime
import math
import random
import http

#防止10054等各种超时
import socket
import time
timesleep = 10
timeout = 20
socket.setdefaulttimeout(timeout)#这里对整个socket层设置超时时间。后续文件中如果再使用到socket，不必再设置

import gzip
import base64
import zlib



header_list = [
    'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:33.0) Gecko/20100101 Firefox/33.0',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; en) Opera 9.50',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0',
    'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)'
]

#爬取单个网址的单页列表数据
def printme(conn,cursor,url,headers):
    global city
    while 1:
        try:
            #showIP()
            changeIP()
            #showIP()
            r = requests.get(url, proxies=proxies, headers=headers,timeout=timeout)
            if r.status_code == 200:
                r.enconding = "utf-8" #设置返回内容的编码
        except urllib.error.URLError as e:
            print(e.reason)
            time.sleep(timesleep)
        except UnicodeDecodeError as e:  
            print('-----UnicodeDecodeError url')
            time.sleep(timesleep)
        except socket.timeout as e:  
            print("-----socket timout")
            time.sleep(timesleep)
        except http.client.BadStatusLine as e:  
            print("-----http.client.BadStatusLine")
            time.sleep(timesleep)
        except ConnectionResetError as e:  
            print("-----ConnectionResetError")
            time.sleep(timesleep)
        except ConnectionAbortedError as e:  
            print("-----ConnectionAbortedError")
            time.sleep(timesleep)
        except IndexError :
            print("貌似被抓到了，再等等")
            #changeIP()
            time.sleep(5)
        except:
            print("未知的异常发生")
            err = open('err.txt','a+')
            err.write(url+'\n')
            err.close()
            changeIP()
        else:           
            soup = BeautifulSoup(r.content,'html.parser',from_encoding='utf-8')
            list = str(soup.findAll('dl',attrs={'class':'list-noimg job-j-list clearfix job-new-list'}))
            t = list.split(',')
            if t:
                #print(t)
                break
   
    count = 0 #统计本页的数据个数
    for tt in t:
        ID = re.findall(r'href="/jianli/(.*)x.htm"',tt)
        name = re.findall(r'<span class="name">(.*)</span>',tt)
        temp = re.findall(r'<span class="bor-right">(.*)</span>',tt)
        sex = str(temp).split(',')[0]
        age = re.findall(r'bor-right">(.*)岁</span>',tt)
        education = re.findall(r'<span class=" bor-right">(.*)</span>',tt)
        experience = re.findall(r'<span>(.*)</span>',tt)
        job = str(re.findall(r'期望职位: </span>(.*)</li>',tt)).replace('|',',')
        area = re.findall(r'期望地区: </span>(.*)</li>',tt)
        pay = re.findall(r'期望月薪: </span>(.*)</li>',tt)
        integrity = re.findall(r'class="fl\sresume-int-col\d">(.*)</span>',tt)
        if not name:
            name = ''
        else:
            name = name[0]
        if not sex:
            sex = ''
        else:
            sex = sex[2:3]
        if not age:
            age = ''
        else:
            age = age[0]
        if not education:
            education = ''
        else:
            education = education[0]
        if not experience:
            experience = ''
        else:
            experience = experience[0]
        if not job:
            job = ''
        else:
            job = job[2:-2]
        if not area:
            area = ''
        else:
            area = area[0]
        if not pay:
            pay = ''
        else:
            pay = pay[0]
        if not integrity:
            integrity = ''
        else:
            integrity = integrity[0]
##        print(ID)
##        print(name)
##        print(sex)
##        print(age)
##        print(education)
##        print(experience)
##        print(job)
##        print(city)        
##        print(pay)
##        print(area)
##        print(integrity)
        sql_insert = """insert into resume(ID,name,sex,age,education,experience,job,city,area,pay,integrity,url)\
        values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        #print(url[:-3])
        if ID:
            #print(ID,name)
            finalID = str(ID)[2:-2]
            finalID = finalID[:10]+finalID[14:]
            temp_url = re.findall(r'http://(.*)/p0g4',url)
            #print(temp_url)
            cursor.execute(sql_insert, (finalID,name,sex,age,education,experience,job,city,area,pay,integrity,temp_url))
            conn.commit()
            count = count + 1
    return count
    
#访问单个网址的分页数据
def traURL(u,count,conn,cursor,headers):  
    if count/32<=1:
        end=1
    else:
        end = math.ceil(count/32)
    for num in range(1,end+1):
        start = time.clock()
        url = u+'o'+str(num)
        if num%30 == 0:
            time.sleep(1*random.randint(5,10))
        #第110页开始不显示数据
        if num ==110:
            ff = open('url.txt','a+')
            ff.write(u+'\n')
            ff.write(str(count)+'\n')
            ff.close()
            break
        while 1:
            count_page = printme(conn,cursor,url,headers)
            if count_page != 0:
                break
            else:
                print('页面抓取失败，重新抓取')
                time.sleep(1*random.randint(1,2))
                #changeIP()
        print("第"+str(num)+"页,爬取"+str(count_page)+"条数据")
        point = open('result.txt','a+')
        point.write(url+'\n')
        point.close()
        end = time.clock()
        print ('耗时：',round(end-start,2),'s')
        #time.sleep(1*random.randint(0,2))

#连接数据库
conn = pymysql.connect(
    host = '127.0.0.1',
    port = 3306,user = 'root',
    passwd = '',
    db = 'ganji',
    charset = 'utf8')
cursor = conn.cursor()

# 代理服务器
proxyHost = "http-cla.abuyun.com"
proxyPort = "9030"
# 代理隧道验证信息
proxyUser = "*"
proxyPass = "*"

proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
  "host" : proxyHost,
  "port" : proxyPort,
  "user" : proxyUser,
  "pass" : proxyPass,
}
proxies = {
        "http"  : proxyMeta,
        "https" : proxyMeta,
        #"Proxy-Switch-Ip" : "yes"
}

#显示当前IP
def showIP():
    h = { "Accept-Encoding": "gzip", }
    currentIP = requests.get("http://proxy.abuyun.com/current-ip", proxies=proxies, headers=h)
    currentIP.enconding = "utf-8"
    currentIP = BeautifulSoup(currentIP.content,'html.parser',from_encoding='utf-8')
    print("当前IP：",str(currentIP).strip())

#切换IP    
def changeIP():
    changIPheaders = {
        "Accept-Encoding": "gzip", #使用gzip压缩传输数据让访问更快
        "Proxy-Switch-Ip" : "yes"}
    while 1:
        try:
            currentIP = requests.get("http://proxy.abuyun.com/switch-ip", proxies=proxies, headers=changIPheaders,timeout=timeout)
            if currentIP.status_code == 200:  
                currentIP.enconding = "utf-8"
                currentIP = BeautifulSoup(currentIP.content,'html.parser',from_encoding='utf-8')
                print("当前IP：",str(currentIP).strip())
                break
        except urllib.error.URLError as e:
            print(e.reason)
            time.sleep(timesleep)
        except UnicodeDecodeError as e:  
            print('-----UnicodeDecodeError url')
            time.sleep(timesleep)
        except socket.timeout as e:  
            print("-----socket timout")
            time.sleep(timesleep)
        except http.client.BadStatusLine as e:  
            print("-----http.client.BadStatusLine")
            time.sleep(timesleep)
        except ConnectionResetError as e:  
            print("-----ConnectionResetError")
            time.sleep(timesleep)
        except ConnectionAbortedError as e:  
            print("-----ConnectionAbortedError")
            time.sleep(timesleep)
        except IndexError :
            print("貌似被抓到了，再等等")
            #changeIP()
            time.sleep(5)
        except:
            print("未知的异常发生")
            time.sleep(5)
##        else:
##            if currentIP.status_code == 200:
##                break        

global city
#读取全部网址
f = open('out.txt','r')
lines = f.readlines()
for line in lines:
    #限定为在校大学生
    url = str(line).strip()+'p0g4'
    print('目标网站：'+url)
    changeIP()
    #showIP()
    headers = {
        "Accept-Encoding": "gzip",
        "User-Agent": header_list[random.randint(0,9)],
        "Referer": url,
    }
    while 1:    
        try:
            r = requests.get(url, proxies=proxies, headers=headers,timeout=timeout)
            if r.status_code == 200:
                r.enconding = "utf-8" #设置返回内容的编码
            soup = BeautifulSoup(r.content,'html.parser',from_encoding='utf-8')
            city_temp = str(soup.findAll('a',attrs={'class':'fc-city'}))
            city = str(re.findall(r'title="">(.*)</a>',city_temp))
            city = city[2:-2]
            #print(city)
            temp = str(soup.findAll('span',attrs={'class':'fc-org'}))
            #print(temp)
            count = int(re.findall(r'<span class="fc-org">(.*)</span>',temp)[0])
        except urllib.error.URLError as e:
            print(e.reason)
            time.sleep(timesleep)
        except UnicodeDecodeError as e:  
            print('-----UnicodeDecodeError url')
            time.sleep(timesleep)
        except socket.timeout as e:  
            print("-----socket timout")
            time.sleep(timesleep)
        except http.client.BadStatusLine as e:  
            print("-----http.client.BadStatusLine")
            time.sleep(timesleep)
        except ConnectionResetError as e:  
            print("-----ConnectionResetError")
            time.sleep(timesleep)
        except ConnectionAbortedError as e:  
            print("-----ConnectionAbortedError")
            time.sleep(timesleep)
        except IndexError :
            print("貌似被抓到了，再等等")
            changeIP()
            time.sleep(5)
        except:
            #防止requests.exceptions.ChunkedEncodingError
            print("未知的异常发生")
            err = open('err.txt','a+')
            err.write(url+'\n')
            err.close()
            time.sleep(5)
            changeIP()
        else:
            break        
    print('简历数:'+str(count))
    if count==0:
        print('\n========================================================\n')
        time.sleep(1*random.randint(1,2))
        continue
    else:
        traURL(url,count,conn,cursor,headers)
    print('\n========================================================\n')
    #time.sleep(1*random.randint(1,2))


#关闭数据库
cursor.close()
conn.close()
f.close()

#爬去指定网址的指定区间页面的数据
def certainURL(URL,begin,end):
    for num in range(begin,end+1):
        start = time.clock()
        url = u+'o'+str(num)
        if num%100 == 0:
            time.sleep(1*random.randint(5,10))            
        count_page = printme(conn,cursor,url,headers)
        print("第"+str(num)+"页,爬取"+str(count_page)+"条数据")
        end = time.clock()
        print ('耗时：',round(end-start,2),'s')
        #time.sleep(1*random.randint(1,2))

#解压
def unzip(data):
    gz = gzip.GzipFile(fileobj=data)
    data = gz.read()
    gz.close()
    return data   





