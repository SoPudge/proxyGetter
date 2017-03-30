# -*- coding: utf-8 -*- 
from urllib import request
from html.parser import HTMLParser
from bs4 import BeautifulSoup
from collections import OrderedDict
import re
import time
class getProxy(object):
    """docstring for getProxyPage"""
    """本类用于抓取代理服务器网页"""
    """包含多个代理服务器的网页"""
    def __init__(self):
        super(getProxy, self).__init__()
        #建立haders
        self._url = 'http://www.xicidaili.com/wt/'
        self._req = request.Request(self._url)
        self._req.add_header('Host','www.xicidaili.com')
        self._req.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:51.0) Gecko/20100101 Firefox/51.0.1 Waterfox/51.0.1')
        #全局变量，存储抓取页面，解析结果
        self._page = ''
        self._proxyStorage = {}

    def getHttp(self):
        #使用代理获取地址
        #proxy_support = request.ProxyHandler({'http':'10.166.1.37:8080'})
        #opener = request.build_opener(proxy_support)
        #request.install_opener(opener)
        #url = 'http://www.xicidaili.com/nt/'
        #读取对应网页
        with request.urlopen(self._req) as f:
            self._page = f.read().decode('utf-8')
        #return self.page

    def decodePage(self):
        #本方法专门解析网页，获取详细Ip信息
        #此处先内部执行getHttp抓取网页
        self.getHttp()
        soup = BeautifulSoup(self._page,'html.parser')
        for i in range(1,101):
            soupFirst = soup.find_all('tr')[i]
            ipaddr = soupFirst.find_all('td')[1].string
            port = soupFirst.find_all('td')[2].string
            if not soupFirst.find('a'):
                zone = '无地区'
            else:
                zone = soupFirst.find('a').string
            isTranspar = soupFirst.find_all(class_="country")[1].string
            ishttp = soupFirst.find_all('td')[5].string
            linkspeed = soupFirst.find_all(class_="bar")[0]['title']
            linktime = soupFirst.find_all(class_="bar")[1]['title']
            alivetime = soupFirst.find_all('td')[-2].string
            updatetime = soupFirst.find_all('td')[-1].string
            self._proxyStorage['%s:%s' % (ipaddr,port)] = {'zone':zone,'isTranspar':isTranspar,'ishttp':ishttp,'linkspeed':linkspeed,'linktime':linktime,'alivetime':alivetime,'updatetime':updatetime}
        return self._proxyStorage


class checkAlive(object):
    '''本类专门用于检测代理的可用性
       原理是使用代理访问baidu，看延迟
    '''
    def __init__(self):
        pass
    def isAlive(self,ishttp,ipport): 
        proxy_support = request.ProxyHandler({ishttp:ipport})
        opener = request.build_opener(proxy_support)
        request.install_opener(opener)
        #读取对应网页用以测试速度
        t1 = time.time()
        with opener.open('http://m.51job.com') as f:
            f.read().decode('utf-8')
        t2 = time.time()
        return ('%s %0.4f ms' % (ipport,(t2 - t1)*1000))


#class storeToSql(object)
#本类存储到sql当中

proxylist = getProxy()
proxyresult = proxylist.decodePage()
checkresult = checkAlive()
print(proxyresult.keys())
for k,v in proxyresult.items():
    print(checkresult.isAlive(v['ishttp'],k))
