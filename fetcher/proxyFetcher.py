# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     proxyFetcher
   Description :
   Author :        JHao
   date：          2016/11/25
-------------------------------------------------
   Change Activity:
                   2016/11/25: proxyFetcher
-------------------------------------------------
"""
__author__ = 'JHao'

import base64
import re
import json
import urllib.parse
from random import randint
from time import sleep

from lxml import etree

from util.webRequest import WebRequest

DEFAULT_HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-US;q=0.7',
    'cache-control': 'max-age=0',
    # 'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="108", "Chromium";v="108"',
    'sec-ch-ua-mobile': '?0',
    # 'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
}

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36 Edg/87.0.664.52",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:88.0) Gecko/20100101 Firefox/88.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36 Edg/86.0.622.69",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36"
]


def _get_random_user_agent():
    random_index = randint(0, len(USER_AGENTS) - 1)
    return USER_AGENTS[random_index]


class ProxyFetcher(object):
    """
    proxy getter
    """

    @staticmethod
    def freeProxy01():
        """
        站大爷 https://www.zdaye.com/dayProxy.html
        """
        start_url = "https://www.zdaye.com/dayProxy.html"
        DEFAULT_HEADERS['User-Agent'] = _get_random_user_agent()
        html_tree = WebRequest().get(start_url, header=DEFAULT_HEADERS, verify=False).tree
        latest_page_time = html_tree.xpath("//span[@class='thread_time_info']/text()")[0].strip()
        from datetime import datetime
        interval = datetime.now() - datetime.strptime(latest_page_time, "%Y/%m/%d %H:%M:%S")
        if interval.seconds < 111300:  # 只采集5分钟内的更新
            target_url = "https://www.zdaye.com/" + html_tree.xpath("//h3[@class='thread_title']/a/@href")[0].strip()
            while target_url:
                _tree = WebRequest().get(target_url, verify=False).tree
                for tr in _tree.xpath("//table//tr"):
                    ip = "".join(tr.xpath("./td[1]/text()")).strip()
                    port = "".join(tr.xpath("./td[2]/text()")).strip()
                    yield "%s:%s" % (ip, port)
                next_page = _tree.xpath("//div[@class='page']/a[@title='下一页']/@href")
                target_url = "https://www.zdaye.com/" + next_page[0].strip() if next_page else False
                sleep(5)

    @staticmethod
    def freeProxy02():
        """
        代理66 http://www.66ip.cn/
        """
        url = "http://www.66ip.cn/"
        resp = WebRequest().get(url, timeout=10).tree
        for i, tr in enumerate(resp.xpath("(//table)[3]//tr")):
            if i > 0:
                ip = "".join(tr.xpath("./td[1]/text()")).strip()
                port = "".join(tr.xpath("./td[2]/text()")).strip()
                yield "%s:%s" % (ip, port)

    @staticmethod
    def freeProxy03():
        """ 开心代理 """
        target_urls = ["http://www.kxdaili.com/dailiip.html", "http://www.kxdaili.com/dailiip/2/1.html"]
        for url in target_urls:
            tree = WebRequest().get(url).tree
            for tr in tree.xpath("//table[@class='active']//tr")[1:]:
                ip = "".join(tr.xpath('./td[1]/text()')).strip()
                port = "".join(tr.xpath('./td[2]/text()')).strip()
                yield "%s:%s" % (ip, port)

    # @staticmethod
    # def freeProxy04():
    #     """ FreeProxyList https://www.freeproxylists.net/zh/ """
    #     url = "https://www.freeproxylists.net/zh/?c=CN&pt=&pr=&a%5B%5D=0&a%5B%5D=1&a%5B%5D=2&u=50"
    #     tree = WebRequest().get(url, verify=False).tree
    #     from urllib import parse
    #
    #     def parse_ip(input_str):
    #         html_str = parse.unquote(input_str)
    #         ips = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', html_str)
    #         return ips[0] if ips else None
    #
    #     for tr in tree.xpath("//tr[@class='Odd']") + tree.xpath("//tr[@class='Even']"):
    #         ip = parse_ip("".join(tr.xpath('./td[1]/script/text()')).strip())
    #         port = "".join(tr.xpath('./td[2]/text()')).strip()
    #         if ip:
    #             yield "%s:%s" % (ip, port)

    @staticmethod
    def freeProxy05(page_count=1):
        """ 快代理 https://www.kuaidaili.com """
        url_pattern = [
            'https://www.kuaidaili.com/free/inha/{}/',
            'https://www.kuaidaili.com/free/intr/{}/'
        ]
        url_list = []
        for page_index in range(1, page_count + 1):
            for pattern in url_pattern:
                url_list.append(pattern.format(page_index))

        for url in url_list:
            tree = WebRequest().get(url).tree
            proxy_list = tree.xpath('.//table//tr')
            sleep(1)  # 必须sleep 不然第二条请求不到数据
            for tr in proxy_list[1:]:
                yield ':'.join(tr.xpath('./td/text()')[0:2])

    @staticmethod
    def freeProxy06():
        """ FateZero http://proxylist.fatezero.org/ """
        url = "http://proxylist.fatezero.org/proxy.list"
        try:
            resp_text = WebRequest().get(url).text
            for each in resp_text.split("\n"):
                json_info = json.loads(each)
                if json_info.get("country") == "CN":
                    yield "%s:%s" % (json_info.get("host", ""), json_info.get("port", ""))
        except Exception as e:
            print(e)

    @staticmethod
    def freeProxy07():
        """ 云代理 """
        urls = ['http://www.ip3366.net/free/?stype=1', "http://www.ip3366.net/free/?stype=2"]
        for url in urls:
            r = WebRequest().get(url, timeout=10)
            proxies = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td>(\d+)</td>', r.text)
            for proxy in proxies:
                yield ":".join(proxy)

    @staticmethod
    def freeProxy08():
        """ 小幻代理 """
        urls = ['https://ip.ihuan.me/address/5Lit5Zu9.html']
        for url in urls:
            r = WebRequest().get(url, timeout=10)
            proxies = re.findall(r'>\s*?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s*?</a></td><td>(\d+)</td>', r.text)
            for proxy in proxies:
                yield ":".join(proxy)

    @staticmethod
    def freeProxy09(page_count=1):
        """ 免费代理库 """
        for i in range(1, page_count + 1):
            url = 'http://ip.jiangxianli.com/?country=中国&page={}'.format(i)
            html_tree = WebRequest().get(url, verify=False).tree
            for index, tr in enumerate(html_tree.xpath("//table//tr")):
                if index == 0:
                    continue
                yield ":".join(tr.xpath("./td/text()")[0:2]).strip()

    @staticmethod
    def freeProxy10():
        """ 89免费代理 """
        r = WebRequest().get("https://www.89ip.cn/index_1.html", timeout=10)
        proxies = re.findall(
            r'<td.*?>[\s\S]*?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})[\s\S]*?</td>[\s\S]*?<td.*?>[\s\S]*?(\d+)[\s\S]*?</td>',
            r.text)
        for proxy in proxies:
            yield ':'.join(proxy)

    @staticmethod
    def wallProxy01():
        """
        PzzQz https://pzzqz.com/
        """
        from requests import Session
        from lxml import etree
        session = Session()
        try:
            index_resp = session.get("https://pzzqz.com/", timeout=20, verify=False).text
            x_csrf_token = re.findall('X-CSRFToken": "(.*?)"', index_resp)
            if x_csrf_token:
                data = {"http": "on", "ping": "3000", "country": "cn", "ports": ""}
                proxy_resp = session.post("https://pzzqz.com/", verify=False,
                                          headers={"X-CSRFToken": x_csrf_token[0]}, json=data).json()
                tree = etree.HTML(proxy_resp["proxy_html"])
                for tr in tree.xpath("//tr"):
                    ip = "".join(tr.xpath("./td[1]/text()"))
                    port = "".join(tr.xpath("./td[2]/text()"))
                    yield "%s:%s" % (ip, port)
        except Exception as e:
            print(e)

    # @staticmethod
    # def freeProxy10():
    #     """
    #     墙外网站 cn-proxy
    #     :return:
    #     """
    #     urls = ['http://cn-proxy.com/', 'http://cn-proxy.com/archives/218']
    #     request = WebRequest()
    #     for url in urls:
    #         r = request.get(url, timeout=10)
    #         proxies = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\w\W]<td>(\d+)</td>', r.text)
    #         for proxy in proxies:
    #             yield ':'.join(proxy)

    # @staticmethod
    # def freeProxy11():
    #     """
    #     https://proxy-list.org/english/index.php
    #     :return:
    #     """
    #     urls = ['https://proxy-list.org/english/index.php?p=%s' % n for n in range(1, 10)]
    #     request = WebRequest()
    #     import base64
    #     for url in urls:
    #         DEFAULT_HEADERS['User-Agent'] = _get_random_user_agent()
    #         r = request.get(url, header=DEFAULT_HEADERS, verify=False, timeout=10)
    #         proxies = re.findall(r"Proxy\('(.*?)'\)", r.text)
    #         for proxy in proxies:
    #             yield base64.b64decode(proxy).decode()

    @staticmethod
    def freeProxy12():
        urls = ['https://list.proxylistplus.com/Fresh-HTTP-Proxy-List-1']
        request = WebRequest()
        for url in urls:
            r = request.get(url, timeout=10)
            proxies = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td>(\d+)</td>', r.text)
            for proxy in proxies:
                yield ':'.join(proxy)

    # @staticmethod
    # def wallProxy02():
    #     request = WebRequest()
    #     try:
    #         resp = request.get("https://spys.one/en/", timeout=20, verify=False).tree
    #         # proxies = resp.xpath('//tbody/tr/td/table[2]/tbody/tr/td[1]/font[@class="spy14"]/text()')
    #         proxies = resp.xpath('//tbody/tr/td/table[2]/tbody/tr/td[1]')
    #         for proxy in proxies:
    #
    #             yield ':'.join(proxy)
    #     except:
    #         pass

    @staticmethod
    def wallProxy03():
        request = WebRequest()
        try:
            resp = request.get("https://free-proxy.cz/en/", timeout=10, verify=False).tree
            proxies = resp.xpath('//table[@id="proxy_list"]/tbody/tr')
            for proxy in proxies:
                ip_base64 = proxy.xpath('./td[1]/script/text()')
                port = proxy.xpath('./td[2]')
                yield "%s:%s" % (base64.b64decode(ip_base64).decode('utf-8'), port)
        except Exception as e:
            print(e)

    @staticmethod
    def wallProxy04():
        request = WebRequest()
        try:
            resp = request.get("https://hidemy.name/en/proxy-list/", timeout=10, verify=False).tree
            proxies = resp.xpath('//div[@class="table_block"]/table/tbody/tr')
            for proxy in proxies:
                ip = "".join(proxy.xpath('./td[1]/text()')).strip()
                port = "".join(proxy.xpath('./td[2]/text()')).strip()
                yield "%s:%s" % (ip, port)
        except Exception as e:
            print(e)

    # @staticmethod
    # def wallProxy05():
    #     request = WebRequest()
    #     try:
    #         DEFAULT_HEADERS['User-Agent'] = _get_random_user_agent()
    #         resp = request.get("https://www.proxydocker.com/", header=DEFAULT_HEADERS, timeout=10, verify=False).tree
    #         token = "".join(resp.xpath('//meta[@name="_token"]/@content')).strip()
    #         import requests
    #         data = {
    #             'token': token,
    #             'country': 'all',
    #             'city': 'all',
    #             'state': 'all',
    #             'port': 'all',
    #             'type': 'all',
    #             'anonymity': 'all',
    #             'need': 'all',
    #             'page': 1,
    #         }
    #         api_resps = requests.post('https://www.proxydocker.com/en/api/proxylist/', headers=DEFAULT_HEADERS,
    #                                   data=data).json()
    #         if api_resps['tows_count'] != 0:
    #             for api_resp in api_resps['proxies']:
    #                 yield "%s:%s" % (api_resp['ip'], api_resp['port'])
    #     except Exception as e:
    #         print(e)

    @staticmethod
    def wallProxy06():
        request = WebRequest()
        try:
            resp = request.get("https://free-proxy-list.net/", timeout=10, verify=False).tree
            tr = resp.xpath('//div[@class="table-responsive"]/div/table/tbody/tr')
            for t in tr:
                ip = "".join(t.xpath('./td[1]/text()')).strip()
                port = "".join(t.xpath('./td[2]/text()')).strip()
                yield "%s:%s" % (ip, port)
        except Exception as e:
            print(e)

    @staticmethod
    def wallProxy07():
        request = WebRequest()
        try:
            pattern = re.compile(r'\"(.*?)\"')
            resp = request.get("https://www.freeproxylists.net/zh/", timeout=10, verify=False).tree
            tr = resp.xpath('//table[@class="DataGrid"]//tr')
            for t in tr:
                ip_encode = "".join(t.xpath('./td[1]/script/text()')).strip()
                if ip_encode == "":
                    continue
                result = pattern.findall(ip_encode)
                if len(result) == 0:
                    continue
                ip = urllib.parse.unquote_plus("".join(result).strip())
                ip = "".join(etree.HTML(ip).xpath("//a/text()")).strip()
                port = "".join(t.xpath('./td[2]/text()')).strip()
                yield "%s:%s" % (ip, port)
        except Exception as e:
            print(e)

    @staticmethod
    def wallProxy08():
        request = WebRequest()
        try:
            resp = request.get("https://www.proxynova.com/proxy-server-list/", timeout=10, verify=False).tree
            tr = resp.xpath('//table[@id="tbl_proxy_list"]/tbody/tr')
            pattern = re.compile(r'[(](.*)[)]', re.S)
            for t in tr:
                ip_encode = "".join(t.xpath('./td[1]/script/text()')).strip()
                if ip_encode == "":
                    continue
                result = pattern.findall(ip_encode)
                if len(result) == 0:
                    continue
                ip = urllib.parse.unquote_plus("".join(result).strip())
                ip = "".join(etree.HTML(ip).xpath("//a/text()")).strip()
                port = "".join(t.xpath('./td[2]/text()')).strip()
                yield "%s:%s" % (ip, port)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    p = ProxyFetcher()
    for _ in p.wallProxy07():
        print(_)
