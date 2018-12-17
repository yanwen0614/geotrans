import numpy as np
import pandas as pd
import random
import pickle
import hashlib
import requests
import random
from time import sleep
import win_unicode_console
win_unicode_console.enable()
import execjs

__doc__ ="""本文件为 调用百度、网易等翻译的函数文件"""


def readgb(file):
    df = pd.DataFrame(pd.read_csv(file,sep="\t"))
    return df


def translateBybaidu(word, fromLang = 'en', toLang = 'zh',bannum=0 ):
    word = str(word).replace("&","and")
    appid = "20171012000087805"
    secretKey = "kYBNLW5KoKTtBRmbyfyl"
    salt = random.randint(32768, 65536)
    sign = appid+word+str(salt)+secretKey
    sign = hashlib.new('md5', sign.encode()).hexdigest()
    translationstr = "http://api.fanyi.baidu.com/api/trans/vip/translate?q={word}&from={fromLang}&to={toLang}&appid={appid}&salt={salt}&sign={md5}"
    a = random.random()
    sleep(2*a)
    translationstr = translationstr.format(word=word, fromLang=fromLang, toLang=toLang,appid=appid,salt=salt,md5=sign)
    try:
        r = requests.get(translationstr)
    except requests.exceptions.ConnectionError as e:
        print(str(e))
        a = random.randint(bannum*6, (bannum+2)*60)
        print("sleep:"+str(a))
        sleep(a)
        return translateBybaidu(word,bannum=bannum+1)
    try:
        a = r.json()["trans_result"][0]["dst"]
    except KeyError as e:
        return str(e)
    return a





class Py4Js():

    def __init__(self):
        self.ctx = execjs.compile("""
        function TL(a) {
        var k = "";
        var b = 406644;
        var b1 = 3293161072;

        var jd = ".";
        var $b = "+-a^+6";
        var Zb = "+-3^+b+-f";

        for (var e = [], f = 0, g = 0; g < a.length; g++) {
            var m = a.charCodeAt(g);
            128 > m ? e[f++] = m : (2048 > m ? e[f++] = m >> 6 | 192 : (55296 == (m & 64512) && g + 1 < a.length && 56320 == (a.charCodeAt(g + 1) & 64512) ? (m = 65536 + ((m & 1023) << 10) + (a.charCodeAt(++g) & 1023),
            e[f++] = m >> 18 | 240,
            e[f++] = m >> 12 & 63 | 128) : e[f++] = m >> 12 | 224,
            e[f++] = m >> 6 & 63 | 128),
            e[f++] = m & 63 | 128)
        }
        a = b;
        for (f = 0; f < e.length; f++) a += e[f],
        a = RL(a, $b);
        a = RL(a, Zb);
        a ^= b1 || 0;
        0 > a && (a = (a & 2147483647) + 2147483648);
        a %= 1E6;
        return a.toString() + jd + (a ^ b)
    };

    function RL(a, b) {
        var t = "a";
        var Yb = "+";
        for (var c = 0; c < b.length - 2; c += 3) {
            var d = b.charAt(c + 2),
            d = d >= t ? d.charCodeAt(0) - 87 : Number(d),
            d = b.charAt(c + 1) == Yb ? a >>> d: a << d;
            a = b.charAt(c) == Yb ? a + d & 4294967295 : a ^ d
        }
        return a
    }
    """)

    def getTk(self,text):
        return self.ctx.call("TL",text)




def translateBygoogle(word):


    def translate(content):
        tk = js.getTk(content)
        if len(content) > 4891:
            return "翻译的长度超过限制！！！"
        param = {'tk': tk, 'q': content}
        headers = {'Accept': '*/*',
               'Accept - Encoding':'gzip, deflate, br',
               'Accept-Language':'zh-CN,zh;q=0.9',
               'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
               "cache-control": "no-cache",
               "referer":"https://translate.google.cn/"
               }
        result = requests.get("""https://translate.google.cn/translate_a/single?client=t&sl=en&tl=zh-CN&hl=zh-CN&dt=at&dt=bd&dt=ex&dt=ld&dt=md&dt=qca&dt=rw&dt=rm&dt=ss&dt=t&ie=UTF-8&oe=UTF-8&source=btn&ssel=0&tsel=0&kc=0""", params=param,headers=headers)
        #返回的结果为Json，解析为一个嵌套列表
        result = result.json()
        return result[0][0][0]
    js = Py4Js()
    bannum = 0
    tag = 1
    aa = 1
    while tag:
        try:
            tag = 0
            aa =  translate(word)
        except :
            tag = 1
            a = random.randint(bannum*6, (bannum+2)*20)
            bannum+=1
            print(word,"\tsleep:"+str(a),"bannum:",bannum)
            sleep(a)
    return aa


if __name__ == '__main__':
    print(translateBybaidu("a conspicuously curved or bent segment of a wadi"))
