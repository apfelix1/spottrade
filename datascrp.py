import urllib.request
import urllib
import time
import random
from higgsboom.FuncUtils.DateTime import *


# 抓取页面方法，调用该方法返回抓取到数据
def read_pageHtml(url):
    file = urllib.request.Request(url,headers={"Upgrade-Insecure-Requests":1, "User-Agent" : "agod/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"} )
    file = urllib.request.urlopen(url)
    data = file.read()
    return data


# 将数据生成txt文件方法 传入保存文件路径 storagePath 以及文件数据 data
def storageToLocalFiles(storagePath, data):
    fhandle = open(storagePath, "wb")
    fhandle.write(data)
    fhandle.close()

tdPeriodList = TradingDays(startDate='20200101', endDate='20201231')

for i in tdPeriodList:
    print(i)
    i = i.replace('-','')
    rd = random.random()
    rd = str(rd)
    url = "http://reportdocs.static.szse.cn/files/text/etf/ETF159901"+i+".txt?random="+rd
    print(url)
    data = read_pageHtml(url)
    storagePath = ".\\tradelist\\159901\\"+'159901'+i+".txt"
    storageToLocalFiles(storagePath, data)
    time.sleep(1)


