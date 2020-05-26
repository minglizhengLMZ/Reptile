# -*- coding: utf-8 -*-
"""
Created on Thu May 14 09:19:53 2020

@author: Flora
"""

'''
1. 解析HTML脚本：
    h1、a：HTML标签
    h1：包含的是标题
    a：包含的是链接以及链接的文字说明
    id、class：特定的属性
    href：网址的链接属性
'''

from bs4 import BeautifulSoup

html_sample = "\
    <html>\
    <body>\
    <h1 id = 'title'>Hello World</h1>\
    <a href = '#' class = 'link'>This is link1</a>\
    <a href = '#link2' class = 'link'>This is link2</a>\
    </body>\
    </html>"
    
soup = BeautifulSoup(html_sample, 'html.parser')
# 2个参数，第一个是HTML脚本，第二个是解析器。

# 提取HTML脚本中所有的文字信息 --------------------------------------------
print(soup.text)
# .text方法输出HTML脚本中的所有文字信息。

# 利用soup.select()提取h1或a标签中的文字信息-------------------------------
soup_1 = soup.select('h1')
# 返回的是包含h1标签的列表。
print(soup_1)
# 打印这个列表
print(soup_1[0].text)
# 访问列表中的文本信息。

soup_2 = soup.select('a')
# 返回的是包含a标签的列表
print(soup_2)
# 打印这个列表
print(soup_2[0].text)
# 访问列表中的第一个元素的文本信息
print(soup_2[1].text)
# 访问列表中的第二个元素的文本信息

# 利用soup.select()语句提取id='title'或class='link'标签中的文字信息---------
alink = soup.select('#title')
# 找出id属性为title的标签，注意id属性的值前加'#'。
# 返回值为列表。
print(alink[0].text)

for link in soup.select('.link'):
    print(link.text)
# 这里找出class属性值为link的标签，返回列表。
# 注意这里class值前要加'.'，由于返回的是含有2个a标签的列表，可以用循环语句遍历

# 利用soup.select()语句提取href属性值
soup_2 = soup.select('a')
for link in soup_2:
    print(link)   # 先打印含a标签的列表
    print(link['href'])   
    # 找出列表中属性为href的值，即网页链接，这里相当于字典中的键值对。
    # 输入键名，即可得到值。
    


'''
2. 抓取新浪军事中国军情标题、时间、链接：
    requests模块：用来读取网页的URL。
    根据Headers中查询的情况，选择get/post/delete/put等方法进行读取。
    res.encoding：表示网页的编码方式，由HTML脚本中的charset属性值表示。
        response -> meta -> charset
    
'''

import requests
from bs4 import BeautifulSoup

res = requests.get('http://roll.mil.news.sina.com.cn/col/zgjq/index.shtml')
res.encoding = 'gb2312'
print(res.text)   # 打印出网页的HTML脚本。

soup = BeautifulSoup(res.text, 'html.parser')
fList = soup.select('.fixList')
# 由HTML脚本可知，新闻标题信息在class='fixList'这个大标签中。
print(fList)
# 结果包含在一个大的列表中。
# 需要的标题、时间、链接包含在<li>标签中。
# 链接、标题由包含在<li>标签里面的<a>标签里。
# 下面用select方法根据其中的hred、class等属性一个一个遍历查找。

# 读取网页里所有需要的新闻标题、时间、链接。
for each in fList[0].select('li'):   # fList是一个列表，所以加一个[0]。
    # 代表取里面第一个元素(就一个元素)，然后select方法寻找里面的li标签。
    # 用循环遍历。
    te = each.text.rstrip()[:-20]
    # 新闻标题。直接用.text方法会将里面的时间文本联通标题一并输出。
    # 这里只取标题，因此将右边20个字符（时间）剔除。
    ti = each.select('.time')[0].text
    # 新闻时间。对每个li标签寻找class='time'的属性，然后取得时间文本。
    a = each.select('a')[0]['href']
    # 新闻链接。从li标签里面寻找a标签，然后再查找href属性的值即为网页链接。
    print(te, ti, a)

# 将结果存储到excel中
import pandas as pd

text = []
for each in fList[0].select('li'):
    alink = {}
    alink['title'] = each.text.rstrip()[:-20]   # 新闻标题
    alink['time'] = each.select('.time')[0].text   # 新闻时间
    alink['url'] = each.select('a')[0]['href']   # 新闻链接
    # print(alink)
    text.append(alink)

df = pd.DataFrame(text)
df.to_csv("text.csv", index = False, encoding='utf_8_sig')



'''
3. 抓取同花顺行情中心的股票数据：
    该网页有反爬虫机制且数据是内置翻页，真正的数据包含在XHR的脚本文件中。
'''

import requests
from bs4 import BeautifulSoup
import time
# 用来指定python每爬取一页数据的停滞时间。
import json
# 对爬取的数据进行处理，保存成字典的格式。
import pandas as pd

headers = {
    'Host':'q.10jqka.com.cn',
    'Referer':'http://q.10jqka.com.cn/',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36',
    'X-Requested-With':'XMLHttpRequest'
    }
url = 'http://q.10jqka.com.cn/index/index/board/all/field/zdf/order/desc/page/2/ajax/1/'
# 给requests.get()函数额外添加参数headers，通常加这几个就可以。
# 有的网站反爬虫强，如拉勾网，还需要额外添加data参数。

res = requests.get(url, headers = headers)
res.encoding = 'gbk'

soup = BeautifulSoup(res.text, 'lxml')

tr_list = soup.select('tbody tr')
# 所有的数据都包含在tbody标签下，而每一只股票又相应的包含在一个tr标签下。
# 通过.select()方法搜索'tbody tr'。
print(tr_list)
# tr_list是一个列表对象。
# 每一只股票的数据是列表的一个元素。

# 爬取第一页的数据--------------------------------------------------------
# 采用一个循环遍历上述列表中的元素，然后将每一只股票的信息构成一个字典存入列表中。
# 每一只股票的每一个信息都在一个td标签中，所以用select方法搜索td。
yeji = []
for each_tr in tr_list:
    td_list = each_tr.select('td')
    data = {
        '股票代码':td_list[1].text,
        '股票简称':td_list[2].text,
        '现价':td_list[3].text,
        '涨幅':td_list[4].text,
        '涨跌':td_list[5].text,
        '涨速':td_list[6].text,
        '换手':td_list[7].text
        }
    yeji.append(data)
print(yeji)

# 根据每一页的URL爬取不同页的数据------------------------------------------
# 写一个循环程序，依次爬取接下来的页码
# 将前面的代码写成函数
def crawl_page(page_id):
    headers = {
        'Host':'q.10jqka.com.cn',
        'Referer':'http://q.10jqka.com.cn/',
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36',
        'X-Requested-With':'XMLHttpRequest'
        }
    
    url = 'http://q.10jqka.com.cn/index/index/board/all/field/zdf/order/desc/page/%s/ajax/1/'%page_id
    
    res = requests.get(url, headers=headers)
    res.encoding = 'gbk' 
    
    soup = BeautifulSoup(res.text, 'lxml')
    # 通过HTML脚本，我们发现所有的数据包含在tbody标签下.
    # 每一支股票又相应的包含在一个tr标签下，
    tr_list = soup.select('tbody tr')      
    #于是可以通过.select方法搜索'tobody tr'.
    
    yeji = []
    for each_tr in tr_list:
        td_list = each_tr.select('td')
        data = {
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

# 采用循环语句，将页码依次代入以爬取不同页数的数据。
# .extend方法是将一个列表添加到另一个列表中。
# time.sleep(10)是将每次爬取时的停滞时间设置为10s。
mydata = []
for page_id in range(1, 4):
    content = crawl_page(page_id)
    mydata.extend(content)
    time.sleep(10)
    
json_result = json.dumps(mydata)
# json.dumps()是将python格式的数据(这里是列表)转化为json编码的数据。
with open('mydata.json', 'w') as f:
    f.write(json_result)
# 用with open创建一个json文件，利用f.write将数据存储到json文件中。
    
with open('mydata.json', 'r') as f:
    data = f.read()
# 利用f.read()读取json文件。

data = json.loads(data)
# 利用json.loads()将json格式的数据转化为python列表格式。
df = pd.DataFrame(data, columns = ['股票代码', '股票简称', '现价',\
                                   '涨幅', '涨跌', '涨速', '换手'])
df.to_csv('mydata.csv', index = False, encoding='utf_8_sig')



'''
4. 抓取京东网站中的手机商品信息（手机名称、价格、店铺、照片等）：
    利用程序模拟浏览器自动打开网页，然后自己输入“手机”进行搜索，等到页面加载
    完毕后，爬取这一页的数据，然后模拟鼠标点击下一页，等下一页加载完毕后再次
    爬取数据。
'''

import re   # 使用正则表达式提取数据
# re模块是python的正则表达式模块，用来进行文本的匹配。
# 提供了一种与select方法相似的文本搜寻路径。
from selenium import webdriver   # 用于打开浏览器
# selenium模块用于浏览器的自动化操作，就是让电脑自动打开网页进行搜索。
# webdriver用于自动打开浏览器。
from selenium.common.exceptions import TimeoutException   
# 用于对打开过程的时间进行控制
from selenium.webdriver.common.by import By   # 用于定位器定位
from selenium.webdriver.support.ui import WebDriverWait   
# 用于设置浏览器打开网页的等待时间和超时时间的判断
from selenium.webdriver.support import expected_conditions as EC
# 用于进行语句的条件判断，提示程序错误等
from bs4 import BeautifulSoup   # 用于解析网页
import time
import pandas as pd

browser = webdriver.Chrome()   
# 实例化chrome浏览器类，可看作打开一个chrome浏览器
wait = WebDriverWait(browser, 10)   # 设置超时时间为10s

'''
    编辑一个search函数，让浏览自自动打开京东商城的网页，然后自动在搜索栏
    搜索手机，并自动打开相应的网页。
    用途：获得商品总页数
'''
def search():   # 定义搜索函数
    try:        # try...except...用于捕捉异常
        browser.get('https://www.jd.com')   # 打开京东页面
        browser.maximize_window()            # 打开至全屏浏览
        input = wait.until(                  # 定位到搜索输入框
            EC.presence_of_element_located((By.CSS_SELECTOR, "#key"))
            )
        '''
        当京东商城的网页打开之后，我们需要让程序判定一下搜索框的位置，以便
        后续将关键词输入进行搜索，EC模块就起到了定位的作用。
        CSS_SELECTOR属性进行定位。
        后面的字符串就是这个属性的值。
        通过打开HTML脚本的Elements部分，将鼠标点击左上角的按钮，再把鼠标移
        至搜索框，即可在HTML脚本中定位到搜索框的位置。
        在HTML对应位置右击copy -> copy selector，将复制到的部分放入python
        中粘贴即可得到"#key"参数值。
        '''
        submit = wait.until(   # 定位到搜索框的搜索键
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#search > div > div.form > button"))
            )
        # 参数值得确定方法和上面相同。
        input.send_keys("手机")   # 输入需要查询的商品
        submit.click()            # 模拟点击
        total = wait.until(       # 显示商品页面共多少页
            EC.presence_of_element_located((By.CSS_SELECTOR, "#J_bottomPage > span.p-skip > em:nth-child(1) >b"))
            )
        return total.text   # 输出商品页面总页数
    except TimeoutException:   # 捕捉超时异常
        return search()        # 若超时，递归调用自身，再次尝试
    
'''
定义翻页函数，让程序自动翻页
'''
def next_page(pageNumber):   # 定义翻页函数
    try:
        browser.execute_script("window.scrollTo(0, 6000)")  
        # 滑动浏览器滚动条至翻页栏
        # 保证网页能够自动下拉到最底部，使得全部商品加载完毕
        # 里面的参数只需改变6000这个数字就好，一般是越大越好
        time.sleep(2)
        input = wait.until(   # 定位到输入需转到的页面输入框
            EC.presence_of_element_located((By.CSS_SELECTOR, "#J_bottomPage > span.p-skip > input"))
            )
        submit = wait.until(  # 定位到翻页确认键
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#J_bottomPage > span.p-skip > a"))
            )
        input.clear()   # 清空页面输入框（将已经输入的页码值进行清理）
        input.send_keys(pageNumber)   # 输入需要跳转的页面
        submit.click()  # 点击翻页确认键
        wait.until(     # 检查是否跳转到需要的页面
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#J_bottomPage > span.p-num > a.curr"),\
                                             str(pageNumber))
            )
        # 当输入的页码已经变成红色的时候，已经翻页成功。
        # 这里多出的参数str(pageNumber)是因为需要将页码数字格式变成字符格式
        return get_products()
    except TimeoutException:   # 捕捉超时异常
        next_page(pageNumber)  # 若超时，递归调用自身，再次尝试
        # 也就是当出现错误时，对当前页码进行重新加载，所以需要递归调用自身一下

'''
定义爬取商品的函数
'''
p = re.compile('<[^>]+>')   # 使用正则表达式去除html标签
# 用re模块写了一个正则表达式的对象，表达的意思是匹配一个或多个以<开始，以>结束
# 并且中间部门不能有>符号的语句。^的意思是取反，[]表示将匹配的内容方法里面。

def get_products():   # 定义抓取页面信息函数
    browser.execute_script("window.scrollTo(0, 9700)")   
    # 滑动浏览器滚动条至翻页栏
    # 当程序自动翻页到指定页后，需要爬取这一页的数据
    # 于是先保证滚动条已下拉至最底部
    time.sleep(2)   # 等待2s，为演示浏览器已滚动至翻页栏
    wait.until(     # 等待页面商品信息加载完成
        EC.presence_of_element_located((By.CSS_SELECTOR, "#J_goodsList"))
        )
    # 进行定位，定位的是该页出现的全部商品
    html = browser.page_source   # 取出当前页的html
    soup = BeautifulSoup(html, 'lxml')   # 用beautisoup解析网页
    items = soup.select("#J_goodsList li.gl-item")   # 提取所需要的的信息
    result = []   # 定义空列表用于存放提取的信息
    for item in items:
        product = {}   # 在循环内部定义字典用于存放提取的信息
        try:   
            # 观察后知道图片链接提取方式不唯一，使用try...except...来解决该问题
            product['image'] = 'https:'+item.select('.p-img a img')[0]['src']
        except:
            product['image'] = 'https:'+item.select('.p-img a img')[0]['data-lazy-img']
        try:
            product['shop'] = item.select('.p-shop a')[0].text
            # 提取店家名称，有些商品店家名称为空，故用try...except来解决
        except:
            product['shop'] = None
        product['price'] = item.select('.p-price strong i')[0].text
        # 提取商品价格
        temp = str(item.select('.p-name.p-name-type-2 em')[0])
        # 为使用正则表达式需将html转成字符串
        print(temp)
        product['item_name'] = str(p.sub("", temp)).strip()
        # 正则表达式提取商品名称
        # p.sub("", temp)表示用正则表达式对象p对temp的字符进行匹配
        # 将匹配到的字符或者字符串用空值代替
        result.append(product)   # 将提取的信息存入列表
    return result   # 返回全部信息

'''
循环遍历每一页，爬取数据
'''
total_pages = int(search())   # 获得商品总页数
data = get_products()   # 获取第一页的商品信息
for i in range(2,4):   # 循环的末尾设置total_pages+1即可爬取所有页面
    temp = next_page(i)
    data.extend(temp)   # 将其他页面的商品信息追加到data列表中
    
'''
存储数据
'''
df = pd.DataFrame(data, columns=['item_name','price','shop','image'])
# 将列表转成数据框
print(len(df))   # 打印数据框行数
print(df.head(5))

df.to_csv("phones.csv", index=False, encoding='utf_8_sig')
