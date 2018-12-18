from Translation import translation
from utils.webtrans import translateBygoogle,translateBybaidu
from utils.Modify import Modify as Modify_
from collections import defaultdict
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
    for key in keys:
        key = " "+key+" "
        if key in rawstr:
            for replacestr in mapdict[key.replace(" ","")]:
                replacestr = " "+replacestr+" "
                subres = rawtrans2mmtan(str(rawstr).replace(key, replacestr, 1), mapdict,keys)
                if isinstance(subres,str):
                    res.append(subres)
                    #rplc.append([replacestr])
                elif isinstance(subres,list):
                    res.extend(subres)
                    #rplc = [ [replacestr]+subrplc for subrplc in subrplcs]
    if res == []:
        res = rawstr #.replace(" ","")
    return res

def mergewp(p_w,rplc):
    res = []
    temp = None
    for i in range(len(p_w)):
        w,p = p_w[i]
        for tran_w in rplc:
            if w in tran_w:
                if w != tran_w:
                    if temp == None:
                        temp = p_w[i]
                        break
                    elif (temp[0]+w) in tran_w:
                        if (temp[0]+w) != tran_w:
                            temp = (temp[0]+w,temp[1]*p)
                            break
                        else:
                            res.append((temp[0]+w,temp[1]*p))
                            temp = None
                            break
                else:
                    res.append(p_w[i])
            else:
                if temp != None:
                    res.append(temp)
                    res.append(p_w[i])
                    temp = None
                    break
        if temp == None:
            res.append(p_w[i])
    return res


print(__name__)
TR = translation("./rule")
#TR.ipa.word2ipa_batch("tran.txt")
Modify = Modify_()
geofile = open("翻译测试文件\\tran.txt","r",encoding="utf8")




if __name__ == "__main__":
    outfile = open("翻译测试文件\\tranout2.txt","w",encoding="utf8") #
    for ii,line in enumerate(geofile):
        line = Modify.phraseCleaning(line.strip()).lower()
        translist = TR.phrasetranslit(line, ii)[-1]
        translist_lit = TR.phrasetranslit(line, ii, checkrule=False)[-1]
        baidu_trans = [  translateBybaidu(lll) \
        for lll,tag in zip(translist_lit.SourceContexts(),translist_lit.transTags()) \
        if tag ==0
        ] # ['WERN', 'ÿ', 'cwrt', '莫特']

        linedict = defaultdict(set)
        for w,i,j,k in zip(line.rsplit(), translist.transContexts(), translist_lit.transContexts(), baidu_trans):
            kk =  [ ww for ww in (i,j,k) if findall("[\u4e00-\u9fa5]|[0-9]",ww)]
            if len(kk):
                linedict[w] = set(kk)

        res = TR.p.parse(line)[0]
        res[0].get_templatestrans(TR.template_tran_hashdict)
        tran, _, un = res[0].sent_tran(tranlist=line.rsplit())
        keys = [ key for key in linedict.keys() if key in tran]
        tran = (" "+tran+" ").replace("  "," ")
        rrrr = rawtrans2mmtan(tran,linedict,keys)
        rrrr = list(set(rrrr))
        rplcs = set()
        for k in keys:
            rplcs.update(linedict[k])
        res2select = []
        print(ii)
        for rl in rrrr:
            rplc = [a for a in rplcs if a in rl]
            aa = getres(rl)
            words = [aaa["word"] for aaa in aa["items"]]
            pro = [aaa["prob"] for aaa in aa["items"]]
            ppl = aa["ppl"]
            p_w = [(w,p) for w,p in zip(words,pro)]
            #p_w = mergewp(p_w,rplc)
            res2select.append((line, rl, p_w, ppl))
            time.sleep(0.2)
        res2select = sorted(res2select,key = lambda x:x[-1])
        for resss in res2select:
            print(*resss,sep="\t",file=outfile)
        outfile.flush()
else:
    fileline = [ (ii,line) for ii,line in enumerate(geofile)]


