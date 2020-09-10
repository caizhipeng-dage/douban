import requests
from bs4 import BeautifulSoup
import re
import time
import pandas as pd


# 定义函数，用来处理User-Agent和Cookie
def ua_ck():
    '''
    网站需要登录才能采集，需要从Network--Doc里复制User-Agent和Cookie，Cookie要转化为字典，否则会采集失败！！！！！
    '''

    user_agent = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36'}

    cookies = 'll="118202"; bid=FsStcocWuPQ; _vwo_uuid_v2=D65179C81F8EE8041E5F8605041534542|e1ed6add019a5cf6cdb06398640e7fe6; ct=y; gr_user_id=43e3a769-ff1c-4abe-b1c3-f7d5b28082de; douban-fav-remind=1; viewed="20438158_10799082_3043970_35174681_26929955_3932365_26886337_27667378_33419041_33385402"; push_doumail_num=0; push_noty_num=0; __utmc=30149280; __utmc=223695111; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1599712590%2C%22https%3A%2F%2Fwww.baidu.com%2Flink%3Furl%3D-946ZDrFNbdKZE0IGp73NUS3eCUaoTpabx75ZzZjM59T_FqZIgo-aeRfe2xfnu1o%26wd%3D%26eqid%3Da1f8e3670000ef4d000000065f59ad4b%22%5D; _pk_ses.100001.4cf6=*; __utma=30149280.1986063068.1597310055.1599704141.1599712590.74; __utmz=30149280.1599712590.74.69.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; __utmb=223695111.0.10.1599712590; __utma=223695111.1305332624.1597310055.1599704141.1599712590.43; __utmz=223695111.1599712590.43.40.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; ap_v=0,6.0; douban-profile-remind=1; __utmv=30149280.17799; __utmb=30149280.8.10.1599712590; dbcl2="223162585:V5BfOpq2kcs"; ck=qnBB; _pk_id.100001.4cf6=991c66698d6e616d.1597310055.43.1599714528.1599704141.'

    # Cookie转化为字典
    cookies = cookies.split('; ')
    cookies_dict = {}
    for i in cookies:
        cookies_dict[i.split('=')[0]] = i.split('=')[1]

    return user_agent, cookies_dict


# 定义函数，用于获取豆瓣top250每一个页面的电影链接，总共有10个页面，每个页面有25部电影
def get_urls(n):
    '''
    n:页面数量，总共有25个页面
    '''
    urls = []
    num = (n-1)*25+1
    for i in range(0, num, 25):
        url = 'https://movie.douban.com/top250?start={}&filter='.format(i)
        urls.append(url)

    return urls


# 定义函数，获取每个页面25部电影的链接
def get_movies_url(url, u_a, c_d):
    '''
    url：每一个页面的链接
    u_a：User-Agent
    c_d：cookies
    '''
    html = requests.get(url,
                        headers=u_a,  # 加载User-Agent
                        cookies=c_d)  # 加载cookie

    html.encoding = html.apparent_encoding  # 解决乱码的万金油方法

    if html.status_code == 200:
        print('网页访问成功，代码：{}\n'.format(html.status_code))

    soup = BeautifulSoup(html.text, 'html.parser')  # 用 html.parser 来解析网页
    items = soup.find('ol', class_='grid_view').find_all('li')
    movies_url = []

    for item in items:
        # 电影链接
        movie_href = item.find('div', class_='hd').find('a')['href']
        movies_url.append(movie_href)

    return movies_url
    time.sleep(0.4)    # 设置时间间隔，0.4秒采集一次，避免频繁登录网页


# 定义函数，获取每一部电影的详细信息
def get_movie_info(href, u_a, c_d):
    '''
    href：每一部电影的链接
    u_a：User-Agent
    c_d：cookies
    '''

    html = requests.get(href,
                        headers=u_a,
                        cookies=c_d)
    soup = BeautifulSoup(html.text, 'html.parser')  # 用 html.parser 来解析网页
    item = soup.find('div', id='content')

    movie = {}  # 新建字典，存放电影信息

    # 电影名称
    movie['电影名称'] = item.h1.span.text

    # 导演、类型、制片国家/地区、语言、上映时间、片长（部分电影这些信息不全，先全部采集，留待数据分析时处理）
    movie['电影其他信息'] = item.find(
        'div', id='info').text.replace(' ', '').split('\n')
    for i in movie['电影其他信息']:
        if ':' in i:
            movie[i.split(':')[0]] = i.split(':')[1]
        else:
            continue

    # 豆瓣评分、评分人数
    movie['评分'] = item.find('div', id='interest_sectl').find(
        'div', class_='rating_self clearfix').find('strong', class_='ll rating_num').text
    movie['评分人数'] = item.find('div', id='interest_sectl').find('div', class_='rating_self clearfix').find(
        'div', class_='rating_sum').find('span', property='v:votes').text

    return movie
    time.sleep(0.4)  # 0.4秒采集一次，避免频繁登录网页


# 设置主函数，运行上面设置好的函数
def main(n):
    '''
    n:页面数量，总共有10个页面
    u_a：User-Agent
    c_d：cookies
    '''
    print('开始采集数据，预计耗时2分钟')

    # 处理User-Agent和Cookie
    login = ua_ck()
    u_a = login[0]
    c_d = login[1]

    # 获取豆瓣top250每一页的链接，共10页
    urls = get_urls(n)
    print('豆瓣10个网页链接已生成！！')

    # 获取每一页25部电影的链接，共250部
    top250_urls = []
    for url in urls:
        result = get_movies_url(url, u_a, c_d)
        top250_urls.extend(result)
    print('250部电影链接采集完成！！开始采集每部电影的详细信息(预计耗时5分钟).......')

    # 获取每一部电影的详细信息
    top250_movie = []  # 储存每部电影的信息
    error_href = []  # 储存采集错误的网址

    for href in top250_urls:
        try:
            movie = get_movie_info(href, u_a, c_d)
            top250_movie.append(movie)
        except:
            error_href.append(href)
            print('采集失败，失败网址是{}'.format(href))

    print('电影详细信息采集完成！！总共采集{}条数据'.format(len(top250_movie)))
    return top250_movie, error_href


# 启动主函数，开始采集数据
result = main(10)
# print(result)  # 查看采集结果


# 保存为本地Excel文件
df = pd.DataFrame(result[0])
df.to_excel('豆瓣电影top250.xlsx')

