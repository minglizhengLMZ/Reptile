# -*- coding: utf-8 -*-
"""
Created on Sun May 17 05:40:41 2020

@author: lenovo
"""

#3.抓取京东网站中的手机商品信息（手机名称，价格，店铺，照片等）

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

#（6）网页加载完毕后，我们想让程序自动翻页，这里定义一个翻页函数，让程序自动翻页，程序详解见
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
    browser.execute_script("window.scrollTo(0,9700)")   
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

#循环历遍每页，爬取数据
total_pages=int(search())        #获得商品总页数
#print(total_pages)
data=get_products()               #获得第一页的商品信息
for i in range(2,4):          #循环的末尾设置为total_pages+1即可爬取所有页面
    temp=next_page(i)
    data.extend(temp)         #将其他页面的商品信息追加到data列表中



#对爬取的数据进行存储
df=pd.DataFrame(data,columns=['item_name','price','shop','image'])   #将列表转换成数据框
print(len(df))          #打印数据框行数
print(df.head(5))        #打印前5行数据
df.to_csv('phones.csv',index=False, encoding='utf_8_sig')






