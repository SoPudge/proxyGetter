# -*- coding: utf-8 -*- 
from urllib import request
from html.parser import HTMLParser
from bs4 import BeautifulSoup
from collections import OrderedDict
import re
class getProxyPage(object):
    """docstring for getProxyPage"""
    """本类用于抓取代理服务器网页"""
    """包含多个代理服务器的网页"""
    def __init__(self):
        super(getProxyPage, self).__init__()
        #建立haders
        self.url = 'http://www.xicidaili.com/nn/'
        self.req = request.Request(self.url)
        self.req.add_header('Host','www.xicidaili.com')
        self.req.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:51.0) Gecko/20100101 Firefox/51.0.1 Waterfox/51.0.1')
        #建立存储字典
        self.proxyStorage = {}

    def getHttp(self):
        #使用代理获取地址
        #proxy_support = request.ProxyHandler({'http':'10.166.1.37:8080'})
        #opener = request.build_opener(proxy_support)
        #request.install_opener(opener)
        #url = 'http://www.xicidaili.com/nt/'
        #读取对应网页
        with request.urlopen(self.req) as f:
            data = f.read().decode('utf-8')
        return data

    def decodePage(self,data):
        #本方法专门解析网页，获取详细Ip信息
        soup = BeautifulSoup(data,'html.parser')
        for i in range(1,101):
            soupFirst = soup.find_all('tr')[i]
            ipaddr = soupFirst.find_all('td')[1].string
            port = soupFirst.find_all('td')[2].string
            if not soupFirst.find('a'):
                zone = ''
            else:
                zone = soupFirst.find('a').string
            isTranspar = soupFirst.find_all(class_="country")[1].string
            linkspeed = soupFirst.find_all(class_="bar")[0]['title']
            linktime = soupFirst.find_all(class_="bar")[1]['title']
            alivetime = soupFirst.find_all('td')[-2].string
            updatetime = soupFirst.find_all('td')[-1].string
            self.proxyStorage['%s:%s' % (ipaddr,port)] = {zone,isTranspar,linkspeed,linktime,alivetime,updatetime}
            print(i,ipaddr,port,zone,isTranspar,linkspeed,linktime,alivetime,updatetime)
        print(self.proxyStorage)


#class checkAlive(object)
#本来做检测代理可用性

#class storeToSql(object)
#本类存储到sql当中

proxypage = getProxyPage()
proxydecode = proxypage.getHttp()
proxypage.decodePage(proxydecode)
#if __name__ == '__main__':
#    proxy = getProxyPage()
#    proxy.getHttp()
