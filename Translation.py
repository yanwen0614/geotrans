
import random
from utils.wordlist import Wordlist
from utils.Modify import Modify
from utils.RuleDict import MappingRule
from utils.templates import loadParser_trandict,fprint
from math import log
from re import sub
from nmt_interfcae import nmt_w2p
from utils.webtrans import translateBybaidu
import logging
import subprocess
import win_unicode_console
from utils.metric import calcScoreAndtran

win_unicode_console.enable()
Modify = Modify()


class ipa(object):
    RuleMapping = MappingRule()
    Syllable_probility   = dict()
    TranslateClass = None
    isloadipafile = False
    ipafile = None
    ipafilelocation = "temp"

    def init_Syllable_probility(self,pro_file):
        with open(pro_file,encoding="utf8") as f:
            for line in f:
                l = line.rsplit(": ")
                self.Syllable_probility[l[0].replace("-","")] = float(l[1])



    def __init__(self,tempfilepath="temp",method = "smt",pro_file="rule/ipaprobility",):
        """
        :param method 生成方式 可选 smt（默认） nmt
        """
        self.init_Syllable_probility(pro_file)
        self.ipafilelocation = tempfilepath
        if method == "smt":
            self.tranfn = self.tran_smt
            import subprocess
        elif method == "nmt":
            self.tranfn = self.tran_nmt
            self.SetNMTmodel("./model/nmt_model_w2p_2_64_200000_bi_at_nadam")
        else:
            raise NotImplementedError

    def SetNMTmodel(self,dir):
        self.TranslateClass = nmt_w2p(dir)


    def tran_smt(self, word):
        sss = "echo '{0}' | mosesdecoder/bin/moses -f  mert-work/moses.ini".format(word)
        s = subprocess.Popen([r".\PowerShellCmd\Mosebyword.bat", sss], stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        stdoutdata, _ = s.communicate(input="a b a n a n".encode("utf-8"))
        s.kill()
        return Modify.IPAmodify(stdoutdata.decode()).rsplit()

    def tran_nmt(self, word):
        return self.TranslateClass.translation(word)[0].rsplit()

    def word2ipa_batch(self, filename,batch =0):
        f = open(filename,mode="r",encoding="utf8")
        wordlist = []
        wordcount = []
        for l in f:
            a = Modify.modifyphrase(l)
            a = a.rsplit()
            wordlist.extend([" ".join(aa).lower() for aa in a])
            wordcount.append(len(a))
        res = self.TranslateClass.translation(wordlist)
        tag = 0
        ff = open(self.ipafilelocation,mode="w",encoding="utf8")
        for r in res:
            if wordcount[0]==0:
                ff.write("\n")
                wordcount = wordcount[1:]
            wordcount[0]-=1
            ff.write(r)
            if wordcount[0]==0:
                ff.write("\n")
                wordcount = wordcount[1:]
            else:
                ff.write(",")
        self.isloadipafile = False


    def loadipafile(self, filename=""):
        if self.isloadipafile:
            return
        if filename=="":
            filename = self.ipafilelocation
        f = open(filename, mode="r", encoding="utf8")
        res = []
        for l in f:
            ll = str(l).rsplit(",")
            lll = [ipa.split() for ipa in ll]
            res.append(lll)
        self.isloadipafile = True
        self.ipafile = res
        return res


    def word2ipa(self, word, isfile = False):
        """
        :word 单词的字符串列表 eg [“a”,"b","c"]
        """
        word = " ".join(word)
        return self.tranfn(word.lower())

    def ipasplit(self, ipalist):

        def dealŋ(temp,ipa):
            if ipa!="ŋ":
                yield  temp + ipa
            else:
                if len(temp)==2:
                    yield temp[0] + ipa
                if len(temp)==1:
                    yield temp+"ː" + ipa
                else:
                    yield temp+ "n"
        temp = ""
        res = dict()
        for i in range(len(ipalist)):
            tt = temp
            for temp in dealŋ(tt,ipalist[i]):
                if temp in self.RuleMapping.IPA2CN.keys():
                    if i != len(ipalist) - 1:
                        a = self.ipasplit(ipalist[i + 1:])
                        res[temp] = a
                    else:
                        res[temp] = ""
        return res

    def ipa2Syllable(self, ipalist):


        def dictflatten(ipadict):
            path = list()
            if ipadict == "":
                return None
            for ipablock in ipadict.keys():
                aa = dictflatten(ipadict[ipablock])
                if aa is None:
                    path.append([ipablock])
                else:
                    for a in aa:
                        tp = [ipablock]
                        tp.extend(a)
                        path.append(tp)
            return path

        def minentropy(pathlist, shortnum=1):
            tmp =  sorted(pathlist, key=lambda x: len(x))[:shortnum]
            res = []
            for ilist in tmp:
                score = 0
                for i in ilist:
                    score += -log(self.Syllable_probility.setdefault(i,6.960104679974387e-06))
                res.append((ilist, score, len(ilist)))
            return sorted(res, key=lambda x: (x[2],x[1]))

        #print(ipalist)
        unkownipa = []
        for ipa in ipalist:
            if ipa not in self.RuleMapping.IPA2CN.keys():
                #print(ipa)
                unkownipa.append(ipa)


        sss = self.ipasplit(ipalist)
        ilist = dictflatten(sss)
        sps = minentropy(ilist, 10)
        if sps ==[]:
            print(ipalist,ilist,sss)
            raise ValueError
        return sps

    def word2Syllable(self ,word, pos):
        if self.tranfn == self.tran_smt:
             _ipa =  self.word2ipa(word)
        else:
            l,c = pos
            if l ==-1:
                _ipa =  self.word2ipa(word)
            else:
                self.loadipafile(self.ipafilelocation)
                _ipa = self.ipafile[l][c]
        _ipa = Modify.IPAmodify(" ".join(_ipa)).split()

        _Syllable = self.ipa2Syllable(_ipa)
        return _Syllable



class translation(object):

    instance_num = 0
    log = ""
    BaseAccuracy = 0.9 # 音译的基础准确度
    p,template_tran_hashdict = loadParser_trandict("./templates/template_tran.txt")
    max_log_p = p.templates.max_log_items-p.templates.log_total_items

    def __init__(self, RuleFolderPath="./rule",ipamethod = "nmt",BaseAccuracy = 0.9):
        self.ipa = ipa(method=ipamethod)
        self.RuleMapping = MappingRule(RuleFolderPath)

    def phrasetrans(self,phrase):
        p,template_tran_hashdict,max_log_p=  self.p,self.template_tran_hashdict,self.max_log_p
        translit_res = self.phrasetranslit(phrase)[-1]
        phrase = Modify.phraseCleaning(phrase)
        parse_res = p.parse(phrase.lower())
        arrc = list()
        for r in parse_res:
            r[0].get_templatestrans(template_tran_hashdict)
            tran,acc,inf = calcScoreAndtran(translit_res,r[0],r[1],max_log_p)
            arrc.append((tran,acc,inf))
            #print(arrc)
        context = phrase.strip()+"\t"+arrc[0][0].replace(" ","")+"\t"+str(arrc[0][1][3])+"\n"

    def phrasetranslit(self,phrase,pos=-1,checkrule = True):
        """
        :phrase 输入的地名短语
        :pos 使用外部音标文件时 pos为短语对应第几行音标
        return
            :string 翻译结果
            :list(int) 翻译标识 未译 -1 音 0 照搬 1  意 2
            :log 翻译关键信息
            : wordlist 对象
        """
        wordlist = Wordlist(Modify.modifyphrase(phrase).rsplit())
        wordlist.updatewordidx()
        return self.tran_wordlist(wordlist,pos,checkrule)

    def tran_wordlist(self, wordlist, line=-1,checkrule = True):
        """
        :phrase 输入的地名短语
        return
            :string 翻译结果
            :list(int) 翻译标识 未译 -1 音 0 照搬 1  意 2
            :log 翻译关键信息
        """
        self.information = ""
        unkown = set()
        if wordlist.length == 1:
            instan_idx = wordlist.CheckinInstance()
            self.instance_num+=len(instan_idx)
            wordlist.instan_idx = instan_idx
            if len(instan_idx) ==1:
                return wordlist.transContext, wordlist.transTag,self.information,wordlist
            if checkrule:
                unkown = wordlist.CheckinRule(self.RuleMapping.EN2CN_Name, 1)
                if not unkown:
                    unkown = wordlist.CheckinRule(self.RuleMapping.EN2CN_Place)
            if unkown or  (not checkrule):
                    tran_res = self.wordtrans(wordlist[0].SourceContext,(line,0))
                    wordlist[0].transContext = tran_res
                    wordlist[0].transTag = 0

            return wordlist.transContext, wordlist.transTag,self.information,wordlist
        """
         CheckinRule 本质上是词形标注
        """
        for word in wordlist:
            if isinstance(word, Wordlist):
                self.tran_wordlist(word,line)
        instan_idx = wordlist.CheckinInstance()
        self.instance_num+=len(instan_idx)
        wordlist.instan_idx = instan_idx
        if checkrule:
            unkown = wordlist.CheckinRule(self.RuleMapping.EN2CN_Name, 1)
            unkown = wordlist.CheckinRule(self.RuleMapping.EN2CN_Place)
        wordlist = Modify.ModifyWordlistBf(wordlist)
        wordlist.CheckSpecialChar()
        for word in wordlist:
            if word.transTag == -1:
                word.transContext = self.wordtrans(word.SourceContext,(line,word.idx-1))
                word.transTag = 0
        #wordlist = Modify.ModifyWordlistAf(wordlist)
        #print(wordlist)  # 去空格

        return wordlist.transContext , wordlist.transTag, self.information,wordlist

    def wordtrans(self, word,pos=-1):

        def MatchPrefix(word):
            pos = 0
            for i in range(1, len(word)):
                if word[:i] in self.RuleMapping.EN2CN_Prefix.keys():
                    pos = i
            if pos == 0:
                return "", word
            Pre_cn = self.RuleMapping.EN2CN_Prefix[word[:pos]]
            self.information += "单词前缀音译:"+word[:pos] +"->"+Pre_cn+"\n"
            return self.RuleMapping.EN2CN_Prefix[word[:pos]], word[pos:]

        def MatchSuffix(word):
            pos = 0
            for i in range(1, len(word)):
                if word[-i:] in self.RuleMapping.EN2CN_Suffix.keys():
                    pos = i
            if pos == 0:
                return "", word
            Suf_cn = self.RuleMapping.EN2CN_Suffix[word[-pos:]]
            self.information += "单词后缀音译:"+word[-pos:] +"->"+Suf_cn+"\n"
            return Suf_cn, word[:-pos]

        self.information += "音译单词:"+word+"\n"
        #Suf, word = MatchSuffix(word)
        #Pre, word = MatchPrefix(word)
        body = self.Syllable2cn(self.ipa.word2Syllable(word.lower(),pos))
        return body[0][0]# Pre + body[0][0] + Suf

    def Syllable2cn(self, Syllable):
        res = list()
        self.information += "单词音节划分:"+str(Syllable[0])+"\n"
        #print(Syllable[0])  #
        for sp in Syllable:
            # #print(sp)
            aaaa = [self.RuleMapping.IPA2CN[lit][0] for lit in sp[0]]
            st = ''.join(aaaa)
            # #print(st)
            res.append((st,sp[1]))
        return res

    def webfiletrans(self,file):
        self.filetrans(file,path_in = ".\\static\\file\\upload",path_out = ".\\static\\file\\trans_result",path_ipatemp = ".\\static\\file\\ipatemp")

    def filetrans(self,file,path_in = "",path_out = "",path_ipatemp = ""):
        self.ipa.ipafilelocation = path_ipatemp
        self.ipa.word2ipa_batch(path_in+"\\"+file)
        f_in = open(path_in+"\\"+file,mode="r")
        f_out = open(path_out+"\\"+file,mode="w",encoding="utf8")
        p,template_tran_hashdict,max_log_p=  self.p,self.template_tran_hashdict,self.max_log_p
        for i,line in  enumerate(f_in):
            if line =="\n":
                context = "\n"
                f_out.write(context)
                f_out.flush()
                continue
            translit_res = self.phrasetranslit(line,i)[-1]

            line = Modify.phraseCleaning(line)
            parse_res = p.parse(line.lower())
            arrc = list()
            for r in parse_res:
                r[0].get_templatestrans(template_tran_hashdict)
                tran,acc,inf = calcScoreAndtran(translit_res,r[0],r[1],max_log_p)
                arrc.append((tran,acc,inf))
                #print(arrc)
            context = line.strip()+"\t"+arrc[0][0].replace(" ","")+"\t"+str(arrc[0][1][3])+"\n"
            f_out.write(context)
            f_out.flush()
        f_out.close()




def Wordtest():
    Translation = translation("./rule",ipamethod="nmt")
    Word = "the Stow on the Wold"
    print(Word)
    aa, _ ,log= Translation.phrasetranslit(Word)
    print(aa)
    print(_) # 音译 意译tag  未译 -1 音 0 照搬 1  意 2
    print(log)

def communicate2bashtest(word = "hello"):
    sss = "echo '{0}' | mosesdecoder/bin/moses -f  mert-work/moses.ini".format(word)
    s = subprocess.Popen([sss], stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
    stdoutdata, _ = s.communicate(input="a b a n a n".encode("utf-8"))
    print(stdoutdata.decode(),str(_))

def fileipatranstest():
    IPA = ipa(method="nmt")
    IPA.word2ipa_batch("./缅甸/mm.txt")
    IPA.loadipafile("temp")




def transtest(ph):
    TR = translation("./rule")
    translist = TR.phrasetranslit(ph)[-1]
    #print(translist)
    p,template_tran_hashdict = loadParser_trandict("./templates/template_tran.txt")
    max_log_p = p.templates.max_log_items-p.templates.log_total_items
    ph = Modify.phraseCleaning(ph)
    res = p.parse(ph.lower())
    arrc = list()
    for r in res:
        r[0].get_templatestrans(template_tran_hashdict)
        tran,acc,inf = calcScoreAndtran(translist,r[0],r[1],max_log_p)
        arrc.append((tran,acc,inf))
    arrc_sorted = sorted(arrc,key = lambda x:x[1][-2],reverse=True) #sqr_acc,sigmod_acc
    print(arrc_sorted[0])


def webfiletranstest():
    TR = translation()
    #TR.webfiletrans("aaa.txt")
    TR.webfiletrans("aaaa.txt")

def filetranstest():
    TR = translation("./rule")
    #TR.ipa.word2ipa_batch("gb_geoname_all.txt")
    p,template_tran_hashdict = loadParser_trandict("./templates/template_tran.txt")
    max_log_p = p.templates.max_log_items-p.templates.log_total_items
    geofile=open("gb_geoname_all.txt","r",encoding="utf8")
    geotransfile = dict()
    geotransfile[0]=open("gb_geoname_all——mt.txt","w",encoding="utf8")
    geotransfile[1]=open("gb_geoname_1——mt.txt","w",encoding="utf8")
    geotransfile[2]=open("gb_geoname_2——mt.txt","w",encoding="utf8")
    geotransfile[3]=open("gb_geoname_3——mt.txt","w",encoding="utf8")
    geotransfile[4]=open("gb_geoname_4——mt.txt","w",encoding="utf8")
    #geotransfile_baidu=open("geotransfile_baidu.txt","w",encoding="utf8")
    #geotransfile_google=open("geotransfile_google.txt","w",encoding="utf8")
    errorfile = open("errorfile.txt","w",encoding="utf8")
    for i,line in enumerate(geofile):
        #try:
        if i%500==0:
            print(i)
        line = Modify.phraseCleaning(line.strip()).lower()
        """
        res=translateBybaidu(line)
        geotransfile_baidu.write(res+"\n")
        geotransfile.flush()
        res=translateBygoogle(line)
        geotransfile_google.write(res+"\n")
        geotransfile.flush()
        """
        translist = TR.phrasetranslit(line,i)[-1]
        res = p.parse(line)
        arrc = list()
        for r in res:
            r[0].get_templatestrans(template_tran_hashdict)
            tran,acc,inf = calcScoreAndtran(translist,r[0],r[1],max_log_p)
            if tran.startswith("-"):
                tran = tran[1:]
            arrc.append((tran,acc,inf))
        arrc_sorted = acc
        print(arrc_sorted[0][0],*arrc_sorted[0][1],*arrc_sorted[0][2],sep="\t",file = geotransfile[0])
        if len(translist)<=4:
            print(line,arrc_sorted[0][0],*arrc_sorted[0][1],*arrc_sorted[0][2],sep="\t",file = geotransfile[len(translist)])
        else:
            print(line,arrc_sorted[0][0],*arrc_sorted[0][1],*arrc_sorted[0][2],sep="\t",file = geotransfile[4])
        """
        except Exception as e:
            print(line,translist,i,file=errorfile)
            print(e,file=errorfile)
        """
    print(TR.instance_num)



if __name__ == '__main__':
    from time import time
    now = time()
    #transtest("Monastery of Saint Nicolas of the Cats")
    webfiletranstest()
    #filetranstest()
    print(time()-now)