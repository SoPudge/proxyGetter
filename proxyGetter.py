# -*- coding: utf-8 -*- 
from urllib import request
from html.parser import HTMLParser
from bs4 import BeautifulSoup
import re
class getProxyPage():
    """docstring for getProxyPage"""
    """本类用于抓取代理服务器网页"""
    """包含多个代理服务器的网页"""
    def __init__(self):
        super(getProxyPage, self).__init__()
        #建立haders
        self.url = 'http://www.xicidaili.com/nt/'
        self.req = request.Request(self.url)
        self.req.add_header('Host','www.xicidaili.com')
        self.req.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:51.0) Gecko/20100101 Firefox/51.0.1 Waterfox/51.0.1')
        #self.req.add_header('Accept','text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
        #建立存储字典
        self.proxyStorage = {}

    def getHttp(self):
        #proxies = {'http': 'http://10.166.1.37:8080/'}
        #opener = request.FancyURLopener(proxies)
        proxy_support = request.ProxyHandler({'http':'10.166.1.37:8080'})
        opener = request.build_opener(proxy_support)
        request.install_opener(opener)
        #url = 'http://www.xicidaili.com/nt/'
        with opener.open(self.req) as f:
            data = f.read().decode('utf-8')
        return data

    def decodePage(self,data):
        soup = BeautifulSoup(data,'html.parser')
        content = soup.select('#ip_list')
        listip = content[0].get_text().split()[10:]
        print(len(listip))
        for i in range(0,99,8):
            self.proxyStorage['%s:%s' % (str(listip[i]),str(listip[i+1]))] = {}
        print(self.proxyStorage)


proxypage = getProxyPage()
proxydecode = proxypage.getHttp()
proxypage.decodePage(proxydecode)
#if __name__ == '__main__':
#    proxy = getProxyPage()
#    proxy.getHttp()
