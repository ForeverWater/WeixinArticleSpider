import requests
from urllib.parse import urlencode
from requests.exceptions import ConnectionError
from requests.exceptions import ConnectTimeout
from pyquery import PyQuery as pq
from bs4 import BeautifulSoup
import lxml
import re

base_url = 'http://weixin.sogou.com/weixin?'
headers = { 'Cookie':'SUV=1498460134109979; SMYUV=1498460134111899; ssuid=1890964740; dt_ssuid=4575662996; IPLOC=CN3502; SUID=FB052A781508990A000000005955F5BE; GOTO=Af22417-3002; ABTEST=8|1511342636|v1; SNUID=E4DDF2A1D9DC8656382EB672D94B1C25; weixinIndexVisited=1; sct=2',
            'Host': 'weixin.sogou.com',
            'Upgrade-Insecure-Requests':'1',
            'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
            }

proxy_pool_url = 'http://127.0.0.1:5010/get/'
proxy = None

keyword = 'iOS开发'

max_count = 5


def get_proxy():
    try:
        responce = requests.get(proxy_pool_url)
        if responce.status_code == 200:
            return responce.text
        return None
    except ConnectionError:
        return None

def get_html(url, count=1):
    print('正在请求',url)
    print('尝试次数',count)
    global proxy
    if count >= max_count:
        print('请求次数太多')
        return None
    try:
        if proxy:
            proxies = {
                'http': 'http://' + proxy
            }
            response = requests.get(url,allow_redirects=False,headers = headers,proxies=proxies,timeout=5)
        else:
            response = requests.get(url,allow_redirects=False,headers = headers)
        # print('HTTP代码', response.status_code)
        if response.status_code == 200:
            return response.text
        if response.status_code == 302:
            print('302')
            proxy = get_proxy()
            if proxy:
                print('获得代理ip：',proxy)
                return get_html(url,count)
            else:
                print('Get Proxy Failed')
                return None

        return None
    except ConnectionError as e:
        proxy = get_proxy()
        count += 1
        print('Error Occurred', e.args)
        return get_html(url,count)
    except requests.exceptions.Timeout:
        proxy = get_proxy()
        count += 1
        print('请求超时：', requests.exceptions.Timeout.args)
        return get_html(url, count)

def get_index(keyword,page):
    data = {
        'query':keyword,
        'type':2,
        'page':page
    }
    queries = urlencode(data)
    url = base_url + queries
    html = get_html(url)
    return html

def parse_index(html):
    print('开始解析标签网页...')
    # pattern = re.compile('txt-box">.*?<h3>.*?href="(.*?)".*?</h3>')
    # items = re.findall(pattern,html)
    doc = pq(html)
    items = doc('.news-box .news-list li .txt-box h3 a').items()
    # soup = BeautifulSoup(html,'lxml')
    # print(soup)
    # items = soup.find('ul',class_='news-list').find_all('li')
    for item in items:
        yield item.attr('href')


def get_article_html(url):
    print('正在获取文章内容...',url)
    try:
        article_headers = {
            'Cookie': 'RK=lKVPu8mfRI; LW_uid=t1L5X0e1z2c3A4951138E0X3z0; eas_sid=V1y500w1A2p3d4V5g2T4P334S5; tvfe_boss_uuid=93388f1d46543e33; pgv_pvi=102194176; sd_userid=94461503753794222; sd_cookie_crttime=1503753794222; LW_sid=x1K570m5X4l6e53151w0Q3m8f6; pgv_si=s966610944; pac_uid=1_642780548; ptui_loginuin=642780548; ptisp=ctc; ptcz=0ed895cfe7d9923f625c03c2b5e8018375336bc694a6599d38c38fd52950bc01; uin=o0642780548; skey=@nrgokCwrW; pt2gguin=o0642780548; pgv_info=ssid=s6511026106&pgvReferrer=; pgv_pvid=1774008720; o_cookie=642780548; _ga=GA1.2.1615192411.1502761867',
            'Host': 'mp.weixin.qq.com',
            'Referer': 'http://weixin.sogou.com/',
            'User-Agent':'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Mobile Safari/537.36'
        }
        responce = requests.get(url,headers = article_headers)
        print('HTTP CODE',responce.status_code)
        if responce.status_code == 200:
            return responce.text
        return None
    except ConnectionError:
        return None

def parse_article(html):
    print('开始解析文章结构...')
    doc = pq(html)
    return {
        'article_title':doc('.rich_media_title').text(),
        'official_account':doc('.rich_media_meta_list a').text(),
        'auther':doc('.rich_media_meta_list em').items()[1].text()
    }

def main():
    for page in range(1,100):
        html = get_index(keyword,page)
        # print(html)
        if html:
            articles = parse_index(html)
            for article_url in articles:
                html = get_article_html(article_url)
                if html:
                     results = parse_article(html)
                     print(results)


if __name__ == '__main__':
    main()