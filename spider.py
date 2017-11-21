import requests
from urllib.parse import urlencode
from requests.exceptions import ConnectionError
from requests.exceptions import ConnectTimeout
from pyquery import PyQuery as pq
from bs4 import BeautifulSoup
import lxml
import re

base_url = 'http://weixin.sogou.com/weixin?'
headers = { 'Cookie':'SUV=1455855914427734; SMYUV=1455855914428687; SUID=0B96CC793120910A0000000057C54695; ssuid=352520587; teleplay_play_records=%C8%FD%BD%A3%C6%E6%D4%B5:1; CXID=73321E1E8313D931285A60A0746ADABF; dt_ssuid=4188476084; ABTEST=0|1511194024|v1; weixinIndexVisited=1; sct=2; IPLOC=CN3502; ppinf=5|1511194273|1512403873|dHJ1c3Q6MToxfGNsaWVudGlkOjQ6MjAxN3x1bmlxbmFtZToyNzolRTUlOTAlQjQlRTglOTklOEUlRTglOTklOEV8Y3J0OjEwOjE1MTExOTQyNzN8cmVmbmljazoyNzolRTUlOTAlQjQlRTglOTklOEUlRTglOTklOEV8dXNlcmlkOjQ0Om85dDJsdUZaV05pSklCdnpJeUd4cnZyLUZqc01Ad2VpeGluLnNvaHUuY29tfA; pprdig=e8ZZSRv1uUF3-5x2E6wsfNS5qtfwdgHNBR91AtLBQLpy8SzLiYddR6f3LJ9OMztcWGA1xK06-NhXK949hLCFkPCrRS7RADyTUz4SnTxfYyC6mvJbK3wG1yPeV0Vq1wmOgZUAt7MecZA1Wm7_FEs1k2wwxbYQuOGwPowVuEO7V6A; sgid=20-32069665-AVoSicqENrz9xYzNiaDjybUv8; SUIR=0FB39CD16660380A226D25966662FBAF; JSESSIONID=aaajGEZApGb8bbjgALv8v; PHPSESSID=4givo4s34g4bsombang3ira8p6; SNUID=3984ABE751540ED120BCE49D51306CC9; ppmdig=1511286493000000734a93957d438dbdd7013fa963aaa632',
            'Host': 'weixin.sogou.com',
            'Upgrade-Insecure-Requests':'1',
            'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
            }

proxy_pool_url = 'http://127.0.0.1:5010/get/'
proxy = None

keyword = '开发'

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
        print('HTTP代码',response.status_code)
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

def main():
    for page in range(1,100):
        html = get_index(keyword,page)
        # print(html)
        if html:
            articles = parse_index(html)
            for article_url in articles:
                print(article_url)


if __name__ == '__main__':
    main()