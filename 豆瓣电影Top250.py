import requests
from bs4 import BeautifulSoup
import re
import time
import pandas as pd

# 获取豆瓣top250每一页的链接


def get_urls(n):
    '''
    n:页面数量，总共有25个页面
    '''

    urls = []
    num = (n - 1) * 25 + 1
    for i in range(0, num, 25):
        url = 'https://movie.douban.com/top250?start={}&filter='.format(i)
        urls.append(url)
    return urls

# 获取每个页面25部电影的链接


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

    soup = BeautifulSoup(html.text, 'html.parser')
    items = soup.find('ol', class_='grid_view').find_all('li')
    movies_url = []

    for item in items:
        # 电影链接
        movie_href = item.find('div', class_='hd').find('a')['href']
        movies_url.append(movie_href)

    return movies_url
    time.sleep(0.4)    # 0.5秒采集一次，避免频繁登录网页

# 获取每一部电影的详细信息


def get_movie_info(href, u_a, c_d):
    '''
    href：每一部电影的链接
    u_a：User-Agent
    c_d：cookies
    '''

    html = requests.get(href,
                        headers=u_a,
                        cookies=c_d)
    soup = BeautifulSoup(html.text, 'html.parser')
    item = soup.find('div', id='content')

    movie = {}  # 新建字典，存放电影信息

    # 电影名称
    movie['电影名称'] = item.h1.span.text

    # 导演、类型、制片国家/地区、语言、上映时间、片长
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
    time.sleep(0.4)  # 0.2秒采集一次，避免频繁登录网页

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
    print('250部电影链接采集完成！！开始采集每部电影的详细信息')

    # 获取每一部电影的详细信息
    top250_movie = []
    for href in top250_urls:
        movie = get_movie_info(href, u_a, c_d)
        top250_movie.append(movie)
    print('250部电影详细信息采集完成！！')

    return top250_movie


if __name__ == '__main__':

    # 启动主函数，开始采集
    result = main(1)
    df = pd.DataFrame(result[0])
    # 保存为本地Excel文件
    df.to_excel('豆瓣top250电影.xlsx')
    
