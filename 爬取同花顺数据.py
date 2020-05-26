# -*- coding: utf-8 -*-
"""
Created on Thu May 14 18:42:43 2020

@author: lenovo
"""

import requests
from bs4 import BeautifulSoup
import time   #time 包是用来指定python每爬取一页数据停滞的时间的，有的网页有反爬虫
#程序，一旦检测到翻页动作太频繁，会自动终止程序的执行的。
import json  #json模块用来对爬取的数据进行处理，保存成字典的格式，是python 常用的数据格式之一。     
import pandas as pd   #常用的数据处理模块


'''
（3）由于这个数据是内置翻页，而刚才那个脚本里面显示的只是一页的数据，当翻至第二页时，
#重新加载网页，这个脚本的数据并没有随之变化，所以需要找到数据存在的真正脚本。
（2）用chrome浏览器开发者工具查看网页架构，找出包含所需数据的HTML脚本：
右击，检查，Network，Doc，然后点击左下方红色方框标注的第一个脚本，点击Response，
下拉脚本发现要爬的数据刚好包含在这个脚本里面。但是这里有一个反爬虫机制：
（4）经过观察，发现真正的数据包含在XHR中的脚本文件中：点击XHR后，再点击一下数据的页码1，
会看到脚本文件中出现一个1/脚本，点击一下页码2会发现又出现一个1/脚本，
所需数据就包含在这些脚本里面，这两个脚本虽然名称一样，但是URL不同，
我们根据不同的URL爬取不同页的数据。
'''
#request headers的内容,在XHR，name，要查询文档的header选项
#爬取第一页的代码
headers={
    'Host':'q.10jqka.com.cn',
    'Referer':'http://q.10jqka.com.cn/',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36',
    'X-Requested-With':'XMLHttpRequest'}

url='http://q.10jqka.com.cn/index/index/board/all/field/zdf/order/desc/page/1/ajax/1/'
res=requests.get(url,headers=headers)
res.encoding='gbk' #编码格式见response Headers的charset
soup=BeautifulSoup(res.text,'lxml')

#通过HTML脚本，我们发现所有的数据包含在tbody标签下，而每一支股票又相应的包含在一个tr标签下，
tr_list=soup.select('tbody tr')      #于是可以通过.select方法搜索’tobody tr’，程序如下图所示，打印出tr_list后会出现一个列表对象
print(tr_list)
yeji=[]
for each_tr in tr_list:
    td_list=each_tr.select('td')
    data={
            '股票代码':td_list[1].text,
            '股票简称':td_list[2].text,
            '股票现价':td_list[3].text,
            '涨跌幅(%)':td_list[4].text,
            '涨跌':td_list[5].text,
            '涨速':td_list[6].text,
            '换手':td_list[7].text,
            }
    yeji.append(data)
print(yeji)


#写一个循环程序，依次爬取接下来的页码
#将前面的代码写成函数
def crawl_page(page_id):
    headers={
        'Host':'q.10jqka.com.cn',
        'Referer':'http://q.10jqka.com.cn/',
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36',
        'X-Requested-With':'XMLHttpRequest'
        }
    
    url='http://q.10jqka.com.cn/index/index/board/all/field/zdf/order/desc/page/%s/ajax/1/'%page_id
    res=requests.get(url,headers=headers)
    res.encoding='gbk' #编码格式见response Headers的charset
    soup=BeautifulSoup(res.text,'lxml')
    
    #通过HTML脚本，我们发现所有的数据包含在tbody标签下，而每一支股票又相应的包含在一个tr标签下，
    tr_list=soup.select('tbody tr')      #于是可以通过.select方法搜索’tobody tr’，程序如下图所示，打印出tr_list后会出现一个列表对象
    yeji=[]
    for each_tr in tr_list:
        td_list=each_tr.select('td')
        data={
                '股票代码':td_list[1].text,
                '股票简称':td_list[2].text,
                '股票现价':td_list[3].text,
                '涨跌幅(%)':td_list[4].text,
                '涨跌':td_list[5].text,
                '涨速':td_list[6].text,
                '换手':td_list[7].text
                }
        yeji.append(data)
    return yeji
crawl_page(1)
'''
接着采用一个循环语句，将页码依次代入以爬取不同页数的数据，
.extend方法是将一个列表添加到另一个列表中，time.sleep(10)是将每次爬取时的停滞时间设置为10s，
即每次爬取一页数据后，停滞10s后再爬取下一页。
'''
YEJI=[]
for page_id in range(1,3):
    page=crawl_page(page_id)
    YEJI.extend(page)      #extend的作用是将列表添加到列表中
    time.sleep(10)    #停滞10s后再爬取下一页,应对反爬虫机制
'''   
这里json.dumps()是将python 格式的数据（这里是列表）转化为json编码的数据，
然后用with open 创建一个json文件，利用f.write将数据存储到json文件中，
利用f.read()就可以读取这个文件，然后利用json.loads()将json格式的数据转化为python列表格式，
最后利用pandas模块，将数据转化成数据框格式，最后一行代码不是将数据存储至Excel中。
'''    
json_result=json.dumps(YEJI)      #将python转换成json数据并存储
with open(r'./yeji.json','w') as fn:
    fn.write(json_result)

with open(r'./yeji.json','r') as fn:  #读取json文件
    data=fn.read()

data=json.loads(data)      #将json数据转换成json列表形式
df=pd.DataFrame(data,columns=[       #将数据转换成pandas形式
        '股票代码',
        '股票简称',
        '股票现价',
        '涨跌幅(%)',
        '涨跌',
        '涨速',
        '换手'])
df.to_csv(r'./yeji.csv',index=False)