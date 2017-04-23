#!/usr/bin/env python3.4

from bs4 import BeautifulSoup
import requests
import chardet
import json
import re
import tkinter
import pickle

url = "http://srh.bankofchina.com/search/whpj/search.jsp"
path="./data.json"
path2="./data.pickle"

def dump(obj,path,compress=1):
    separators=(",",":")if compress else None
    indent = None if compress else 4
    with open(path,"w") as f:
        json.dump(obj,f,separators=separators,indent=indent)
def dump2(obj,path):
    with open(path,"wb") as f:
        pickle.dump(obj,f)

def load(path):
    with open(path) as f:
        return json.load(f)
def load2(path):
    with open(path,"rb") as f:
        return pickle.load(f)

class DataLike:
    def __repr__(self):
        if hasattr(self,"data"):return repr(self.data)
    def __str__(self):
        if hasattr(self,"data"):return str(self.data)
    
class DictLike(DataLike):
    def __init__(self,**kw):
        self.data = {}
        for k,v in kw.items():
            self.data[k] = v
    def __getitem__(self,key):
        return dict.get(self.data,key)
    def __setitem__(self,key,value):
        return dict.__setitem__(self.data,key,value)
    def __delitem__(self,key):
        return dict.__delitem__(self.data,key)
    def update(self,*E,**F):
        dict.update(self.data,*E,**F)

class MyHeaders(DictLike):
    pass

def setheaders():
    headers=MyHeaders()
    Host = "srh.bankofchina.com"
    Agent = "Mozilla/5.0 (Windows NT 5.1; rv:52.0) Gecko/20100101 Firefox/52.0"
    Accept = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    Language = "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3"
    Encoding = "gzip, deflate"
    Referer = "http://srh.bankofchina.com/search/whpj/search.jsp"
    Cookie = "JSESSIONID=0000pk6nJhH7uAHEITKamS6XW8n:-1"
    Connection = "keep-alive"
    dic = {"Host":Host,
           "User-Agent":Agent,
           "Accept":Accept,
           "Accetp-Language":Language,
           "Accept-Encoding":Encoding,
           "Referer":Referer,
           "Cookie":Cookie,
           "Connection":Connection,
           }
    headers.update(dic)
    return headers.data

class Pjname:
    data = {}
    def detect(self):
        print("decting pjname")
        r = requests.get("http://www.boc.cn/sourcedb/whpj/")
        r.close()
        c = chardet.detect(r.content)['encoding']
        b = BeautifulSoup(r.content,"html5lib",from_encoding=c)
        s = b.find("select",attrs={"id":"pjname"})
        o=s.findAll("option")
        for p in o:
            self.data[p.text]=p["value"]
    def __init__(self):
        if not self.data:
            self.detect()

class Date(DataLike):
    def __init__(self,data=""):
        import time
        today = time.strftime("%Y-%m-%d",time.localtime())
        data = data or today
        try:
            data = int(data)
        except:
            pass
        else:
            data = "%s-%d-%d"%(data//10000%9999 or today[:4],data%10000//100%13 or 1,data%100%32 or 1)
        self.data = data

class Rate:
    def __init__(self):
        self.pjname=1323
        self.name="JPY"

class Para(DictLike):
    def __init__(self,data=None):
        data = data or {"erectDate":Date().data,
                        "nothing":Date().data,
                        "pjname":"1323",
                        "page":"1",
                        }
        self.data = data
            

def getRate(url=url,data=None,headers=setheaders()):
    import time
    data = data or Para(data).data
    r = requests.post(url,data=data,headers=headers)
    r.close()
    c = chardet.detect(r.content)['encoding']
    b = BeautifulSoup(r.content,"html5lib",from_encoding=c)
    d = b.find("div",class_="BOC_main publish")
    tb = d.find("tbody")
    tr = tb.findAll("tr")
    data=[1-(20-int(re.findall("(?:m_nRecordCount = )(\d+)",r.content.decode(c))[0]))//20]
    for tt in tr[1:]:
        td = tt.findAll("td")
        if not td:break
        if len(td) < 8: continue
        data.append((td[0].text,
                     float(td[1].text),
                     float(td[2].text),
                     float(td[3].text),
                     float(td[4].text),
                     float(td[5].text),
                     float(td[6].text),
                     time.strptime(td[7].text,"%Y.%m.%d %H:%M:%S")))
    return tuple(data)

def getBS(url):
    import time
    time.sleep(0.1)
    req = requests.get(url)
    res = BeautifulSoup(req.content,"html5lib")
    req.close()
    return res


def main():
    pass

if __name__ == "__main__":
    main()
