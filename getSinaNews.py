# 获取新闻的标题，内容，时间和评论数
# https://www.cnblogs.com/zengbojia/p/7220190.html

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import json
import pandas

def getNewsdetial(newsurl):
    try:
        res = requests.get(newsurl)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text,'html.parser')
        newsTitle = soup.select('.main-title')[0].text.strip()
        nt = datetime.strptime(soup.select('.date')[0].contents[0].strip(),'%Y年%m月%d日 %H:%M')
        newsTime = datetime.strftime(nt,'%Y-%m-%d %H:%M')
        newsArticle = getnewsArticle(soup.select('.article p'))
        newsAuthor = soup.select('.show_author')[0].contents[0].strip()
        keywords = soup.select('.keywords')[0].get('data-wbkey')
    except IndexError:
        newsTitle = None
        newsTime = None
        newsArticle = None
        newsAuthor = None
        keywords = None
    return newsTitle,newsTime,newsArticle,newsAuthor,keywords

def getnewsArticle(news):
    newsArticle = []
    for p in news:
         newsArticle.append(p.text.strip())
    return '\n'.join(newsArticle)

# 获取评论数量

def getCommentCount(newsurl):
    m = re.search('doc-i(.+).shtml',newsurl)
    newsid = m.group(1)
    commenturl = 'http://comment5.news.sina.com.cn/page/info?version=1&format=js&channel=gn&newsid=comos-{}&group=&compress=0&ie=utf-8&oe=utf-8&page=1&page_size=20'
    comment = requests.get(commenturl.format(newsid))   #将要修改的地方换成大括号，并用format将newsid放入大括号的位置
    jd = json.loads(comment.text.lstrip('var data='))
    return jd['result']['count']['total']


def getNewsLinkUrl():
#     得到异步载入的新闻地址（即获得所有分页新闻地址）
    urlFormat = 'http://api.roll.news.sina.com.cn/zt_list?channel=news&cat_1=gnxw&cat_2==gdxw1||=gatxw||=zs-pl||=mtjj&level==1||=2&show_ext=1&show_all=1&show_num=22&tag=1&format=json&page={}&callback=newsloadercallback&_=1501000415111'
    url = []
    for i in range(1,10):
        res = requests.get(urlFormat.format(i))
        jd = json.loads(res.text.lstrip('  newsloadercallback(').rstrip(');'))
        url.extend(getUrl(jd))     #entend和append的区别
    return url

def getUrl(jd):
#     获取每一分页的新闻地址
    url = []
    for i in jd['result']['data']:
        url.append(i['url'])
    return url

# 取得新闻时间，编辑，内容，标题，评论数量并整合在total_2中
def getNewsDetial():
    title_all = []
    author_all = []
    commentCount_all = []
    article_all = []
    time_all = []
    keywords_all = []
    detail = []
    url_all = getNewsLinkUrl()
    for url in url_all:
        print(url)
        detail = getNewsdetial(url)
        if detail[0] == None:
            continue
        print(detail[0] + ' ' + detail[1])
        title_all.append(detail[0])
        time_all.append(detail[1])
        article_all.append(detail[2])
        author_all.append(detail[3])
        keywords_all.append(detail[4])
        commentCount_all.append(getCommentCount(url))
    total_2 = {'a_title':title_all,'b_article':article_all,'c_commentCount':commentCount_all,'d_time':time_all,'e_editor':author_all,'f_keywords':keywords_all}
    return total_2

# ( 运行起始点 )用pandas模块处理数据并转化为excel文档

df = pandas.DataFrame(getNewsDetial())
df.to_excel('news2.xlsx')