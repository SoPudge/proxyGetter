# -*- coding: utf-8 -*- 
from urllib import request
from html.parser import HTMLParser
from bs4 import BeautifulSoup
from collections import OrderedDict
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
        #requests sessions
        self._s = requests.Session()

    @property
    def getxici(self):
        #读取对应网页
        proxyStorage = {}
        url = 'http://www.xicidaili.com/nn/'
        r = self._s.get(url,headers = self._xiciheaders)
        page = r.text

        soup = BeautifulSoup(page,'html.parser')
        soupFirst = soup.find_all('tr')
        l = map(lambda x:x.stripped_strings,soupFirst)
        n = (m for m in [i for i in l])
        print(n)
        #此处通过stripped_strings方法获取不带空格的，所有html标签的text，为一个generator
        #验证templist长度，确认抓取内容中不含地理位置，如不含有则手动添加，保证list长度统一
        #return proxyStorage

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
        self._c.execute('CREATE TABLE IF NOT EXISTS proxy (ipaddr TEXT,port TEXT,ishttp TEXT,istranspar TEXT,zone TEXT)')
        #这里设置sqlite主键自增，id INTEGER PRIMARY KEY，则插入一个null值得时候，会实现自动新增主键
        #同时只存储ip地址，端口，类型，匿名情况和地区情况

    def storeToSQL(self):
        try:
            proxyvalues = []
            for k,v in self._kw.items():
                proxyvalues.append(v)
            self._c.executemany('INSERT INTO proxy VALUES (?,?,?,?,?)',proxyvalues)
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
    print(p.getxici)
