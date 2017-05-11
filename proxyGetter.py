# -*- coding: utf-8 -*- 
from urllib import request
from html.parser import HTMLParser
from bs4 import BeautifulSoup
from collections import OrderedDict
from lxml import html
import requests
import re
import time
import sqlite3

class getProxy(object):
    """docstring for getProxyPage"""
    """本类用于抓取代理服务器网页"""
    """包含多个代理服务器的网页"""
    def __init__(self):
        #头headers
        self._xiciheaders = {'Host':'www.xicidaili.com','User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:51.0) Gecko/20100101 Firefox/51.0.1 Waterfox/51.0.1'}
        self._kdailiheaders = {'Host':'www.kuaidaili.com','User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:51.0) Gecko/20100101 Firefox/51.0.1 Waterfox/51.0.1'}
        #requests sessions
        self._s = requests.Session()

    @property
    def getxici(self):
        #读取对应网页
        #xpath获取代理内容为list，通过循环将list放到对应的dict当中，格式为ipport:ip,addr,http,trans，同时通过update合并字典去重复
        d = {}
        da = {}
        urls = ['http://www.xicidaili.com/nn/','http://www.xicidaili.com/nt/','http://www.xicidaili.com/wn/','http://www.xicidaili.com/wt/']
        for url in urls:
            r = self._s.get(url,headers = self._xiciheaders)
            page = r.text

            tree = html.fromstring(page)
            t = tree.xpath('//tr/td[position()<=3]/text() | //tr/td[5]/text() | //tr/td[6]/text()')        
            for i in range(0,len(t),4):
                d['%s:%s' % (t[i],t[i+1])] = (t[i],t[i+1],t[i+3],t[i+2])
            da.update(d)
        return da

    @property
    def getkdaili(self):
        d = {}
        da = {}
        keyurl = 'http://www.kuaidaili.com/free/'
        keywords = ['inha/1','inha/2','inha/3','intr/1','intr/2','intr/3','outha/1','outha/2','outha/3','outtr/1','outtr/2','outtr/3',]
        urls = [keyurl+x for x in keywords]
        for url in urls:
            time.sleep(1)
            r = self._s.get(url,headers = self._kdailiheaders)
            page = r.text

            tree = html.fromstring(page)
            t = tree.xpath('//td[position()<=4]/text()')        
            for i in range(0,len(t),4):
                d['%s:%s' % (t[i],t[i+1])] = (t[i],t[i+1],t[i+3],t[i+2])
            da.update(d)
        return da

class storage(object):
    """本类存储到sql当中""" 
    #传入一个字典，存储到数据库当中，并且可以读取
    #init当中预先定义一个数据库表，可判断如果存在则跳过，否则新建
    #store应当是添加数据，而不是覆盖数据
    def __init__(self):
        self._sqlname = 'proxy.db'
        self._conn = sqlite3.connect(self._sqlname)
        self._c = self._conn.cursor()
        self._c.execute('CREATE TABLE IF NOT EXISTS proxy (ipaddr TEXT,port TEXT,ishttp TEXT,istranspar TEXT)')
        #这里设置sqlite主键自增，id INTEGER PRIMARY KEY，则插入一个null值得时候，会实现自动新增主键
        #同时只存储ip地址，端口，类型，匿名情况

    def storeToSQL(self,**kwargs):
        kw = kwargs 
        try:
            proxyvalues = []
            for k,v in kw.items():
                proxyvalues.append(v)
            self._c.executemany('INSERT INTO proxy VALUES (?,?,?,?)',proxyvalues)
            #以上是插入对象到数据库
            self._c.execute('DELETE FROM proxy WHERE rowid NOT IN (SELECT MIN(rowid) FROM proxy GROUP BY ipaddr)')
            #每次插入之后，做去除重复项操作，rowid为自带属性，并按照ipaddr删除
        except sqlite3.Error as e:
            print('An error occourd: %s' % e.args[0])
        finally:
            self._c.execute('SELECT COUNT(ipaddr) FROM proxy')
            result = self._c.fetchall()[0][0]
            #以上查询当前数据表中一共有多少条数据
            self._c.close()
            self._conn.commit()
            self._conn.close()
        return result

class checkAlive(object):
    '''本类专门用于检测代理的可用性
       原理是使用代理访问baidu，看延迟
       存储到专门的数据库，ipaddr,site,lag,statu,updatetime
    '''
    def __init__(self):
        self._url = 'http://m.51job.com'
        self._urlconfirm = '51job'
        self._sqlname = 'proxy.db'
        self._conn = sqlite3.connect(self._sqlname)
        self._c = self._conn.cursor()
        self._c.execute('CREATE TABLE IF NOT EXISTS status (ipaddr TEXT,site TEXT,lag TEXT,statu TEXT,updatetime TEXT)')
        self._c.execute('SELECT ishttp,ipaddr,port FROM proxy')
        self._httpipport = self._c.fetchall()
        #将http ipaddr port 结果放在list当中，以便调用，这样不会重复读取数据库
        self._c.execute('SELECT COUNT(ipaddr) FROM proxy')
        self._proxynum = self._c.fetchall()[0][0]
        #这里获取一共有多少条代理需要验证
        
    def isAlive(self):
        num = 1
        insertvalue = []
        try:
            for row in self._httpipport:
                ishttp = row[0]
                ipport = ('%s:%s' % (row[1],row[2]))
                #循环读取数据库当中的ishttp和ipport字段
                proxy_support = request.ProxyHandler({ishttp:ipport})
                opener = request.build_opener(proxy_support)
                request.install_opener(opener)
                #读取对应网页用以测试速度
                print('%s/%s 正在验证代理：%s:%s ...' % (num,self._proxynum,row[1],row[2]))
                t1 = time.time()
                with opener.open(self._url) as f:
                    if self._urlconfirm in str(f.info()):
                        sitestatu = 'OK'
                    else: sitestatu = 'NOK'
                    t2 = time.time()
                lagtime =('%0.2f' % ((t2-t1)*1000))
                insertvalue.append((row[1],self._url,lagtime,sitestatu,'2017'))
                #这里将需要写入数据库的内容先放在list当中，方便后续一次性execuatemany写入
                print('访问验证结果为 %s，延迟 %s ms' % (sitestatu,lagtime))
                num = num + 1

        finally:
            self._c.executemany('INSERT INTO status VALUES (?,?,?,?,?)',insertvalue)
            self._c.execute('SELECT COUNT(ipaddr) FROM status')
            result = self._c.fetchall()[0][0]
            print('合计验证了 %s 条结果' % result)
            #查询写入多少条结果
            self._c.close()
            self._conn.commit()
            self._conn.close()


if __name__ == '__main__':
    p = getProxy()
    plist = p.getxici
    plist1 = p.getkdaili
    print(len(plist))
    print(len(plist1))
    plist.update(plist1)
    s = storage()
    l = s.storeToSQL(**plist)
    print(l)
