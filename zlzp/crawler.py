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
    global businessKind
    while 1:
        try:
            changeIP()
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
            list_zp = soup.findAll('div',attrs={'class':'details_container'})
            break
    count = 0 #统计本页的数据个数
    for i in list_zp:
        #print(i)
        i = str(i)
        title = re.findall('target="_blank" title=".*">(.*)</a></span>',i)
        ID = re.findall(r'type="checkbox" value="(.*)"/>',i)
        #print(ID)
        release_time=re.findall(r'class="release_time">(.*)</span>',i)
        size=re.findall(r'<span>公司规模：(.*)</span>',i)
        detailurl = str(re.findall(r'<span class="post"><a href="(.*)" target="_blank"',i))[2:-2]
        nature = re.findall(r'<span>公司性质：(.*)</span>',i)
        company = re.findall(r'target="_blank" title=".*">(.*) </a></span>',i)
        salary = re.findall(r'class="salary">(.*)</span>',i)
        experience = re.findall(r'<span>工作经验：(.*)</span>',i)
        education = re.findall(r'<span>学历：(.*)</span>',i)
        #print(detailurl)
        if detailurl=="":
            continue
        if not title:
            title = ''
        else:
            title = title[0]
        if not ID:
            ID = ''
        else:
            ID = ID[0]
        if not size:
            size = ''
        else:
            size = size[0]
        if not nature:
            nature = ''
        else:
            nature = nature[0]
        if not company:
            company = ''
        else:
            company = company[0]
        if not salary:
            salary = ''
        else:
            salary = salary[0]
        if not experience:
            experience = ''
        else:
            experience = experience[0]
        if not education:
            education = ''
        else:
            education = education[0]
        sql_insert = """insert into employee(ID,title,company,salary,release_time,experience,education,size,nature,city,area,positionKind,businessKind,requireNum,url,detailurl)\
                    values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        if ID:
            try:
                #print(title)
                cursor.execute(sql_insert,(ID,title,company,salary,release_time,experience,education,size,nature,city,'','',businessKind,'',url,detailurl))
                conn.commit()
            except pymysql.err.InternalError:
                print('数据编码有问题')
            count = count + 1
    return count

#访问单个网址的分页数据
def traURL(u,count,conn,cursor,headers):  
    if count/60<=1:
        end=1
    else:
        end = math.ceil(count/60)
    for num in range(1,end+1):
        start = time.clock()
        url = u+'p'+str(num)
        #if num%30 == 0:
        #    time.sleep(1*random.randint(5,10))
        #第101页开始不显示数据
        if num ==101:
            ff = open('url.txt','a+')
            ff.write(u+'\n')
            ff.write(str(count)+'\n')
            ff.close()
            break
        count = 0
        while 1:
            count_page = printme(conn,cursor,url,headers)
            if count_page != 0:
                break
            else:
                print('页面抓取失败，重新抓取')
                time.sleep(1*random.randint(1,2))
                #changeIP()
            count = count + 1
            if count ==3:
                break
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
    db = 'zlzp',
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
            time.sleep(5)
        except:
            print("未知的异常发生")
            time.sleep(5)
            
##url='http://jobs.zhaopin.com/aba/in210500/p4'           
##headers = {
##        "Accept-Encoding": "gzip",
##        "User-Agent": header_list[random.randint(0,9)],
##        "Referer": url,
##    }
##
##printme(conn,cursor,url,headers)
            
global city
global businessKind
#读取全部网址
f = open('out.txt','r')
lines = f.readlines()
for line in lines:
    url = str(line).strip()
    print('目标网站：'+url)
    #changeIP()
    headers = {
        "Accept-Encoding": "gzip",
        "User-Agent": header_list[random.randint(0,9)],
        "Referer": url,
    }
    while 1:    
        try:
            r = requests.get(url,proxies=proxies, headers=headers,timeout=timeout)
            if r.status_code == 200:
                r.enconding = "utf-8" #设置返回内容的编码
            soup = BeautifulSoup(r.content,'html.parser',from_encoding='utf-8')
            city_temp = str(soup.findAll('h1'))
            city = str(re.findall(r'<h1>(.*)人才网',city_temp))[2:-2]
            #print(city)
            number_temp = str(soup.findAll('span',attrs={'style':'float: right;'}))
            number = str(re.findall(r'(\d{1,6})条',number_temp))[2:-2]
            number = int(number)
            #print(number)
            businessKind = str(re.findall(r'条'+city+"(.*)招聘信息",number_temp)[0])
            #print(businessKind)
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
    print('招聘数:'+str(number))
    if number==0:
        print('\n========================================================\n')
        time.sleep(1*random.randint(1,2))
        continue
    else:
        traURL(url,number,conn,cursor,headers)
        #break
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





