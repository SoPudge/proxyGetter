# -*- coding: utf-8 -*- 
from urllib import request
from html.parser import HTMLParser
from bs4 import BeautifulSoup
from collections import OrderedDict
import re
import time
import sqlite3
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
        #读取对应网页
        with request.urlopen(self._req) as f:
            self._page = f.read().decode('utf-8')
        #return self.page

    def decodePage(self):
        #本方法专门解析网页，获取详细Ip信息
        #此处先内部执行getHttp抓取网页
        self.getHttp()
        soup = BeautifulSoup(self._page,'html.parser')
        soupFirst = soup.find_all('tr')
        templist = []
        #此处通过stripped_strings方法获取不带空格的，所有html标签的text，为一个generator
        #验证templist长度，确认抓取内容中不含地理位置，如不含有则手动添加，保证list长度统一
        for i in range(1,len(soupFirst)):
            for text in soupFirst[i].stripped_strings:
                templist.append(text)
            if len(templist) == 7:
                pass
            else:
                templist.insert(2,'无地理位置')
        #此处将list按照位置加入倒字典当中并返回
            self._proxyStorage['%s:%s' % (templist[0],templist[1])] = (
                                                                        templist[0],
                                                                        templist[1],
                                                                        templist[2],
                                                                        templist[3],
                                                                        templist[4],
                                                                        templist[5],
                                                                        templist[6]
                                                                      )
        #此处重置templist，否则每次添加内容到同一个templist当中，导致字典只能获取第一个代理的值
            templist = []
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
            status = f.status
            t2 = time.time()
        return ('%s %0.4fms %s' % (ipport,(t2 - t1)*1000,status))


class storage(object):
    """本类存储到sql当中""" 
    #传入一个字典，存储到数据库当中，并且可以读取
    #init当中预先定义一个数据库表，可判断如果存在则跳过，否则新建
    #store应当是添加数据，而不是覆盖数据
    def __init__(self,**kwargs):
        self._kw = kwargs 
        self._sqlname = 'proxy.db'
        self._conn = sqlite3.connect(self._sqlname)
        self._c = self._conn.cursor()
        #self._c.execute('CREATE TABLE xicidaili (ipaddr TEXT PRIMARY KEY,port TEXT,zone TEXT,istranspar TEXT,ishttp TEXT,alivetime TEXT, updatetime TEXT)')

    def storeToSQL(self):
        try:
            proxyvalues = []
            for k,v in self._kw.items():
                proxyvalues.append(v)
            self._c.executemany('INSERT INTO xicidaili VALUES (?,?,?,?,?,?,?)',proxyvalues)
        except sqlite3.Error as e:
            print('An error occourd: %s' % e.args[0])
        finally:
            result = self._c.rowcount
            self._c.close()
            self._conn.commit()
            self._conn.close()
        return result



proxylist = getProxy()
proxyresult = proxylist.decodePage()
#checkresult = checkAlive()
print(proxyresult)
storageproxy = storage(**proxyresult)
print(storageproxy.storeToSQL())
#for k,v in proxyresult.items():
#    print(checkresult.isAlive(v[4],k))
