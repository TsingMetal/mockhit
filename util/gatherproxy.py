import os
import re

import requests
from bs4 import BeautifulSoup

from orm.proxy import Proxy, session


class ProxyGather(object):

    def gather_proxy(self):
        pattern = re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,5}')
        basc_url = 'https://free-proxy-list.com/?search=1&page={}&port=&type%5B%5D=https&speed%5B%5D=3&connect_time%5B%5D=3&up_time=0&search=Search'
        urls = [basc_url.format(i+1) for i in range(5)]
        for url in urls:
            doc = requests.get(url)
            if doc.status_code == 200:
                bsobj = BeautifulSoup(doc.text, 'html.parser')
                links = bsobj.find_all(alt=pattern)
                for link in links:
                    ip, port = tuple(link['alt'].split(':'))
                    country = link.find_parent()\
                            .find_next_sibling()\
                            .find_next_sibling()\
                            .find_next_sibling()\
                            .text.strip()
                    print(f'get {ip}:{port}, {country}')
                    self.save_proxy(ip, port, country)
            else:
                print(f"open link fail of link doesn't exist:\n{url}")

    def save_proxy(self, ip, port, country):
        proxy = Proxy(ip=ip, port=port, country=country)
        session.add(proxy)
        try:
            session.commit()
            print('saved')
        except Exception:
            print('skipped')
            session.rollback()


        


if __name__ == '__main__':
    gather = ProxyGather()
    gather.gather_proxy()
