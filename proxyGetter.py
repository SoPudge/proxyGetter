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
        self._url = 'http://www.xicidaili.com/wn/'
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
                                                                        templist[4],
                                                                        templist[3],
                                                                        templist[2]
                                                                      )
        #此处重置templist，否则每次添加内容到同一个templist当中，导致字典只能获取第一个代理的值
            templist = []
        return self._proxyStorage

class checkAlive(object):
    '''本类专门用于检测代理的可用性
       原理是使用代理访问baidu，看延迟
       存储到专门的数据库，ipaddr,site,lag,statu,updatetime
    '''
    def __init__(self):
        self._url = 'http://m.51job.com'
        self._sqlname = 'proxy.db'
        self._conn = sqlite3.connect(self._sqlname)
        self._c = self._conn.cursor()
        self._c.execute('CREATE TABLE IF NOT EXISTS status (ipaddr TEXT,site TEXT,lag TEXT,statu TEXT,updatetime TEXT)')
        self._httpipport = self._c.execute('SELECT ishttp,ipaddr,port FROM proxy')
        #将http ipaddr port 结果放在生成器当中，以便调用
        self._c.execute('SELECT COUNT(ipaddr) FROM proxy')
        self._proxynum = self._c.fetchall()[0][0]
        #这里获取一共有多少条代理需要验证
        
    def isAlive(self):
        num = 1
        insertvalue = []
        try:
            for row in self._c.execute('SELECT ishttp,ipaddr,port FROM proxy'):
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
                    sitestatu = f.status
                    t2 = time.time()
                lagtime =('%0.2f' % ((t2-t1)*1000))
                insertvalue.append((row[1],self._url,lagtime,sitestatu,'2017'))
                #这里将需要写入数据库的内容先放在list当中，方便后续一次性execuatemany写入
                print('验证过成功，延迟 %s ms' % lagtime)
                num = num + 1

        except sqlite3.Error as e:
            print('An error occourd in checkstatus: %s' % e.args[0])

        finally:
            self._c.executemany('INSERT INTO status VALUES (?,?,?,?,?)',insertvalue)
            self._c.execute('SELECT COUNT(ipaddr) FROM status')
            result = self._c.fetchall()[0][0]
            print('合计验证了 %s 条结果' % result)
            #查询写入多少条结果
            self._c.close()
            self._conn.commit()
            self._conn.close()


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



proxylist = getProxy()
proxyresult = proxylist.decodePage()
print(proxyresult)
storageproxy = storage(**proxyresult)
print(storageproxy.storeToSQL())
checkresult = checkAlive()
checkresult.isAlive()
