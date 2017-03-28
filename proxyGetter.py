# -*- coding: utf-8 -*- 
from urllib import request
class getProxyPage():
    """docstring for getProxyPage"""
    """本类用于抓取代理服务器网页"""
    """包含多个代理服务器的网页"""
    def __init__(self):
        super(getProxyPage, self).__init__()
    def getHttp(self):
        #proxies = {'http': 'http://10.166.1.37:8080/'}
        #opener = request.FancyURLopener(proxies)
        #proxy_support = request.ProxyHandler({'http':'10.166.1.37:8080'})
        #opener = request.build_opener(proxy_support)
        #request.install_opener(opener)
        url = 'http://cn-proxy.com/'
        with request.urlopen(url) as f:
            print(f.status,f.reason)
            for k,v in f.getheaders():
                print(k,v)




proxy = getProxyPage()
proxy.getHttp()
if __name__ == '__main__':
    proxy = getProxyPage()
    proxy.getHttp()
