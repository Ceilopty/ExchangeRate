#!/usr/bin/env python3.4
__author__ = "Ceilopty"

"""
get exchange rate from www.BOC.cn
"""

from bs4 import BeautifulSoup
import requests
import chardet
import json
import re
import tkinter
import pickle
from os import path as ospath

url = "http://srh.bankofchina.com/search/whpj/search.jsp"

"""
path_j="./data.json"
path_p="./data.pickle"
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
"""

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
    ins = None
    pjn = ("英镑","港币","美元","瑞士法郎","新加坡元","瑞典克朗","丹麦克朗","挪威克朗",
           "日元","加拿大元","澳大利亚元","欧元","印尼卢比","南非兰特","澳门元","菲律宾比索",
           "泰铢","印度卢比","新西兰元","韩元","卢布","阿联酋迪拉姆","巴西里亚尔","沙特里亚尔",
           "新台币","土耳其里拉","林吉特")
    cur = ("GBP","HKD","USD","CHF","SGD","SEK","DKK","NOK","JPY","CAD","AUD","EUR",
           "IDR","ZAR","MOP","PHP","THB","INR","NZD","KRW","RUB","AED","BRL","SAR",
           "TWD","TRY","MYR",)
    pjmap = dict(zip(cur,pjn))
    pjmap_re = dict(zip(pjn,cur))
    data = {}
    @classmethod
    def dumpj(cls,compress=1):
        separators=(",",":") if compress else None
        indent = None if compress else 4
        with open(ospath.join(".","pjname.json"),"w") as f:
            json.dump(cls.data,f,separators=separators,indent=indent)
    @staticmethod
    def loadj():
        with open(ospath.join(".","pjname.json")) as f:
            return json.load(f)
    @classmethod
    def dumpp(cls):
        with open(ospath.join(".","pjname.pickle"),"wb") as f:
            pickle.dump(cls.data,f)
    @staticmethod
    def loadp():
        with open(ospath.join(".","pjname.pickle"),"rb") as f:
            return pickle.load(f)
    @classmethod
    def detect(cls):
        print("decting pjname")
        r = requests.get("http://www.boc.cn/sourcedb/whpj/")
        r.close()
        c = chardet.detect(r.content)['encoding']
        b = BeautifulSoup(r.content,"html5lib",from_encoding=c)
        s = b.find("select",attrs={"id":"pjname"})
        o=s.findAll("option")
        for p in o:
            cls.data[p.text]=p["value"]
        cls.data.pop("选择货币")
    def __new__(cls,data=None):
        if not cls.ins:
            cls.ins = super().__new__(cls)
            if not cls.data:
                try:
                    cls.data=cls.loadp() or cls.loadj()
                except:
                    cls.detect()
                    cls.dumpj()
                    cls.dumpp()
        if isinstance(data,int):data=str(data)
        return cls.data.get(cls.pjmap.get(data,data),data if data in cls.data.values() else "1323")

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

class RateDatum(tuple):
    n_fields = 8
    n_sequence_fields = 8
    n_unnamed_fields = 0
    def __new__(cls,*args):
        import time
        from collections import Iterable
        if len(args) is not 1 or not isinstance(args[0],Iterable):
            raise ValueError("")
        args=[x for x in args[0]]
        if len(args) is not 8 : raise IndexError("")
        args[0] = Pjname.pjmap_re[args[0]]
        args[7] = time.strptime(args[7],"%Y.%m.%d %H:%M:%S")
        return super().__new__(cls,args)
    @property
    def cu(self):
        "Currency Name."
        return self[0]
    @property
    def b2(self):
        "Bank Spot exchange buying price. Exchange bid rate."
        return self[1]
    @property
    def b1(self):
        "Bank Cash buying price. Cash bid rate."
        return self[2]
    @property
    def a2(self):
        "Bank Spot exchange selling price. Exchange ask rate."
        return self[3]
    @property
    def a1(self):
        "Bank Cash selling price. Cash ask rate."
        return self[4]
    @property
    def ms(self):
        "SAFE middle rate"
        return self[5]
    @property
    def mb(self):
        "BOC middle rate"
        return self[6]
    @property
    def ti(self):
        "Publish time"
        return self[7]
    def __str__(self):
        import time
        temp=tuple(x if x else "N/A" for x in self[:7])
        return "RateData(%s %s %s %s %s %s %s %s)"%(temp+(time.strftime("%Y.%m.%d %H:%M:%S",self.ti),))
    __repr__ = __str__
    def csv(self):
        return ",".join(self[:7])+",%s-%s-%s %s:%02d:%02d"%self[7][:6]

class Rate:
    #prefix_path
    path = ospath.join(".","data")
    @property
    def path_j(self):
        return ospath.join(self.path,"%s.json"%self.cur)
    @property
    def path_p(self):
        return ospath.join(self.path,"%s.pickle"%self.cur)
    def __init__(self,cur="JPY"):
        self.pjname=Pjname(cur)
        self.cur=cur
        self.RecordCount=0
        try:
            data = self.lp(self.path_p) or self.lj(self.path_j)
        except:
            data = []
        else:
            print("Read data")
        finally:
            self.data = data
    @staticmethod
    def mod(num=0):return 1-(20-num)//20
    @property
    def n_pages(self):return self.mod(self.RecordCount)
    def dj(self,compress=1):
        try:
            data = self.lj()
        except:
            obj = self.data
        else:
            obj,sub = list(data),list(self.data) if len(data)>len(self.data) else list(self.data),list(data)
            for x in sub:
                if not x in obj:
                    obj.append(x)
        finally:
            separators=(",",":") if compress else None
            indent = None if compress else 4
            with open(self.path_j,"w") as f:
                json.dump(obj,f,separators=separators,indent=indent)
    def dp(self):
        try:
            data = self.lp()
        except:
            obj = self.data
        else:
            obj,sub = list(data),list(self.data) if len(data)>len(self.data) else list(self.data),list(data)
            for x in sub:
                if not x in obj:
                    obj.append(x)
        finally:
            with open(self.path_p,"wb") as f:
                pickle.dump(obj,f)
    def lj(self):
        with open(self.path_j) as f:
            return json.load(f)
    def lp(self):
        with open(self.path_p,"rb") as f:
            return pickle.load(f)
    @staticmethod
    def getRate(url=url,data=None,headers=setheaders()):
        data = Para(data).data
        r = requests.post(url,data=data,headers=headers)
        r.close()
        c = chardet.detect(r.content)['encoding']
        b = BeautifulSoup(r.content,"html5lib",from_encoding=c)
        d = b.find("div",class_="BOC_main publish")
        tb = d.find("tbody")
        tr = tb.findAll("tr")
        data=[int(re.findall("(?:m_nRecordCount = )(\d+)",r.content.decode(c))[0])]
        for tt in tr[1:]:
            td = tt.findAll("td")
            if not td:break
            if len(td) < 8: continue
            data.append(RateDatum(map(lambda x:x.text,td)))
        return tuple(data)
    def get(self,para=None):
        import time
        data=Rate.getRate(data=para)
        self.RecordCount=data[0]
        self.data.extend(data[1:])
        if int(para["page"])<self.n_pages:pass

class Para(DictLike):
    pj = Pjname
    def __init__(self,data=None,*args,**kw):
        data = data or {}
        ii = isinstance
        if ii(data,dict):
            kw.update(data)
            data = {"erectDate":kw.get("erectDate",Date().data),
                    "nothing":kw.get("nothing",Date().data),
                    "pjname":Pjname(kw.get("pjname","1323")),
                    "page":kw.get("page","1")}
        if args:data=(data,)+args
        if ii(data,Para):data=data.data
        if ii(data,tuple):
            data = {"erectDate":Date(data[0]).data,
                    "nothing":Date(data[1]).data,
                    "pjname":Pjname(data[2]),
                    "page":data[3]}
        self.data = data


def main():
    pass

if __name__ == "__main__":
    main()
