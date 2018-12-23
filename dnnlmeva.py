from Translation import translation
from utils.webtrans import translateBygoogle,translateBybaidu
from utils.Modify import Modify as Modify_
from collections import defaultdict, OrderedDict
from re import findall
import win_unicode_console

win_unicode_console.enable()

from aip.nlp import AipNlp
import time
import random
""" 你的 APPID AK SK """
APP_ID = "11531120"
API_KEY = 'RbM59mzor1ezkHLp1QiDswIp'
SECRET_KEY = 'hmawRt625C4Isjgbc6snw3cbZa5CGjqN'

client = AipNlp(APP_ID, API_KEY, SECRET_KEY)

def getres(word,bannum=0):
    try:
        aa = client.dnnlm(word)
        return aa
    except  ConnectionError as e:
        a = random.randint(1, bannum+3)
        print("sleep:"+str(a))
        time.sleep(a)
        return getres(word, bannum=bannum+1)


def rawtrans2mmtan(rawstr, mapdict,keys):
    res = []
    keytag = [ 0 for i in keys]
    replclist = []
    def GetAllrplc(rawlist,rplcs):
        res = []
        if rawlist==[]:
            return [ [i] for i in rplcs]
        for ll in rawlist:
            for rplc in rplcs:
                res.append(ll+[rplc] )
        return res
    for key in keys:
        replclist = GetAllrplc(replclist,mapdict[key])

    for replc in replclist:
        rawstr__ = rawstr
        keytag = [ 0 for i in keys]
        for i,key_replacestr in enumerate(zip(keys,replc)):
            key,replacestr = key_replacestr
            idx = mapdict[key].index(replacestr)
            if idx!=0:
                keytag[i] = 1
            key = " "+key+" "
            replacestr = " "+replacestr+" "
            replacestr = replacestr.replace("的","")
            rawstr__ =  str(rawstr__).replace(key, replacestr, 1)
        yield rawstr__,keytag,replc


def pro2ppl(pro,length):
    return pro**(-1/length)

def mergewp(p_w,rplc):
    res = []
    temp = None
    for i in range(len(p_w)):
        w,p = p_w[i]
        intag = 0
        for tran_w in rplc:
            if w in tran_w:
                intag = 1
                if w != tran_w:
                    if temp == None:
                        temp = p_w[i]
                        break
                    elif (temp[0]+w) in tran_w:
                        if (temp[0]+w) != tran_w:
                            temp = (temp[0]+w,temp[1]*p)
                            break
                        elif (temp[0]+w) == tran_w:
                            res.append((temp[0]+w,temp[1]*p))
                            temp = None
                            break
                elif w == tran_w:
                    res.append(p_w[i])
        if temp == None and intag == 0:
            res.append(p_w[i])
            intag =0
    return res


print(__name__)
TR = translation("./rule")
#TR.ipa.word2ipa_batch("翻译测试文件\\tran.txt")
Modify = Modify_()
geofile = open("翻译测试文件\\tran.txt","r",encoding="utf8")



def lcs(a,b):
    lena=len(a)
    lenb=len(b)
    c=[[0 for i in range(lenb+1)] for j in range(lena+1)]
    flag=[[0 for i in range(lenb+1)] for j in range(lena+1)]
    for i in range(lena):
        for j in range(lenb):
            if a[i]==b[j]:
                c[i+1][j+1]=c[i][j]+1
                flag[i+1][j+1]='ok'
            elif c[i+1][j]>c[i][j+1]:
                c[i+1][j+1]=c[i+1][j]
                flag[i+1][j+1]='left'
            else:
                c[i+1][j+1]=c[i][j+1]
                flag[i+1][j+1]='up'
    def printLcs(flag,a,i,j):
        res = ''
        if i==0 or j==0:
            return ""
        if flag[i][j]=='ok':
            res += printLcs(flag,a,i-1,j-1)
            res += a[i-1]
        elif flag[i][j]=='left':
            res += printLcs(flag,a,i,j-1)
        else:
            res += printLcs(flag,a,i-1,j)
        return res

    return printLcs(flag,a,lena,lenb)




if __name__ == "__main__":
    #outfile = open("翻译测试文件\\tranout2.txt","w",encoding="utf8") #
    for ii,line in enumerate(geofile):
        """
        if ii<14:
            continue
        """
        line = Modify.phraseCleaning(line.strip()).lower()
        line = Modify.modifyphrase(line)
        translist = TR.phrasetranslit(line, ii)[-1]
        translist_lit = TR.phrasetranslit(line, ii, checkrule=False)[-1]
        instanTags = [0 for i in range(translist.length)]
        for i in translist.instan_idx:
            instanTags[i] = 1

        SourceContexts = translist.SourceContexts()
        res = TR.p.parse(line)[0]
        res[0].get_templatestrans(TR.template_tran_hashdict)
        tran, _, un = res[0].sent_tran(tranlist=line.rsplit())
        keys = [ key for key in tran.rsplit() if key in SourceContexts]
        tran = (" "+tran+" ").replace("  "," ")
        linedict = OrderedDict()
        for key in keys:
            idx = SourceContexts.index(key)
            tt = (translist_lit.transContexts()[idx],translist.transContexts()[idx],translateBybaidu(key))
            kk =  [ ww for ww in tt if findall("[\u4e00-\u9fa5]",ww)]
            if len(kk)==3:
                if len(lcs(tt[0],tt[-1])) >= len(tt[0])/2 and instanTags[idx]: #判断translateBybaidu是否为音译 用最长子序列的长度判断
                    if tt[0] != tt[1]:
                        linedict[key] = tt[:-1]
                    else:
                        linedict[key] = tt[:1]
                else:
                    if tt[0] != tt[1]:
                        linedict[key] = tt
                    else:
                        linedict[key] = [tt[0],tt[-1]]

            elif kk:
                if tt[0] != tt[1]:
                    linedict[key] = tt[:-1]
                else:
                    linedict[key] = tt[:1]

        rrrr = rawtrans2mmtan(tran,linedict,keys)
        res2select = []
        print(ii)
        print(keys)
        for rl in rrrr:
            tran_str,keytag,rplc = rl
            aa = getres(tran_str)
            words = [aaa["word"] for aaa in aa["items"]]
            pro = [aaa["prob"] for aaa in aa["items"]]
            ppl = aa["ppl"]
            p_w = [(w,p) for w,p in zip(words,pro) if w != " " ]
            p_w = mergewp(p_w,rplc)
            prosss = 1
            for i in p_w:
                prosss = prosss*i[1]
            ppl = pro2ppl(prosss,len(p_w))
            print('\t',len(p_w),ppl)
            res2select.append((line, rl, p_w, ppl))
            time.sleep(0.2)
        """
        res2select = sorted(res2select,key = lambda x:x[-1])
        for resss in res2select:
            print(*resss,sep="\t",file=outfile)
        outfile.flush()
        """
else:
    fileline = [ (ii,line) for ii,line in enumerate(geofile)]


