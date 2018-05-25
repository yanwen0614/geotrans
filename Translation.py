
import random
import subprocess
import sys
from utils.wordlist import Wordlist
from utils.Modify import Modify
from utils.RuleDict import MappingRule

import win_unicode_console
win_unicode_console.enable()


class translation(object):

    i = 0
    Modify = Modify()
    RuleMapping = MappingRule()
    log = ""

    def __init__(self, RuleFolderPath="./rule"):
        pass

    def phrasetrans(self, phrase):
        self.log = ""
        wordlist = Wordlist(self.Modify.modifyphrase(phrase).rsplit())
        if wordlist.length == 1:
            aaaaaa = self.wordtrans(wordlist[0].SourceContext)
            wordlist[0].transTag = 0
            return aaaaaa,wordlist.transTag(),self.log
        wordlist = self.Modify.ModifyWordlistBf(wordlist)
        unkown = wordlist.CheckinRule(self.RuleMapping.EN2CN_Name, 1)
        unkown = wordlist.CheckinRule(self.RuleMapping.EN2CN_Place)
        wordlist.CheckSpecialChar()
        for word in wordlist:
            if word.transTag == -1:
                word.transContext = self.wordtrans(word.SourceContext)
                word.transTag = 0
        wordlist = self.Modify.ModifyWordlistAf(wordlist)
        
        return "".join(wordlist.transContext()), wordlist.transTag(),self.log

    def wordtrans(self, word):

        def MatchPrefix(word):
            pos = 0
            for i in range(1, len(word)):
                if word[:i] in self.RuleMapping.EN2CN_Prefix.keys():
                    pos = i
            if pos == 0:
                return "", word
            Pre_cn = self.RuleMapping.EN2CN_Prefix[word[:pos]]
            self.log += "单词前缀音译:"+word[:pos] +"->"+Pre_cn+"\n"
            return self.RuleMapping.EN2CN_Prefix[word[:pos]], word[pos:]

        def MatchSuffix(word):
            pos = 0
            for i in range(1, len(word)):
                if word[-i:] in self.RuleMapping.EN2CN_Suffix.keys():
                    pos = i
            if pos == 0:
                return "", word
            Suf_cn = self.RuleMapping.EN2CN_Suffix[word[-pos:]]
            self.log += "单词后缀音译:"+word[-pos:] +"->"+Suf_cn+"\n"
            return Suf_cn, word[:-pos]

        print(word)
        self.log += "音译单词:"+word+"\n"
        Suf, word = MatchSuffix(word)
        Pre, word = MatchPrefix(word)
        self.log += ""
        body = self.Ipa2cn(self.GetIPA(word.lower()))
        return Pre + body[0] + Suf

    def GetIPA(self, word):
        word = " ".join(word)
        sss = "echo '{0}' | mosesdecoder/bin/moses -f  mert-work/moses.ini".format(word)
        s = subprocess.Popen([r".\PowerShellCmd\Mosebyword.bat", sss], stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        stdoutdata, _ = s.communicate(input="a b a n a n".encode("utf-8"))
        return self.Modify.IPAmodify(stdoutdata.decode()).rsplit()

    def ipasplit(self, ipalist):
        temp = ""
        res = dict()
        for i in range(len(ipalist)):
            temp = temp + ipalist[i]
            if temp in self.RuleMapping.IPA2CN.keys():
                if i != len(ipalist) - 1:
                    a = self.ipasplit(ipalist[i + 1:])
                    res[temp] = a
                else:
                    res[temp] = ""
        return res

    def Ipa2cn(self, ipalist):
        print(ipalist)
        res = list()
        for ipa in ipalist:
            if ipa not in self.RuleMapping.IPA2CN.keys():
                print(ipa)

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

        def ShortPath(pathlist, shortnum=1):
            return sorted(pathlist, key=lambda x: len(x))[:shortnum]
        
        sss = self.ipasplit(ipalist)
        ilist = dictflatten(sss)
        sps = ShortPath(ilist, 10)
        self.log += "单词音节划分:"+str(sps[0])+"\n"
        for sp in sps:
            # print(sp)
            aaaa = [self.RuleMapping.IPA2CN[lit][0] for lit in sp]
            st = ''.join(aaaa)
            # print(st)
            res.append(st)
        return res

    def filetrans(self, file):
        path_in = "static/file/upload"
        path_out = "static/file/trans_result"
        f_in = open(path_in+"/"+file,mode="r")
        f_out = open(path_out+"/"+file,mode="w")
        for line in f_in:
            a = line
            try:
                res = self.phrasetrans(a)
            except :
                context = a[:-1]+"\t"+"Error：音标生成错误"+"\n";
                f_out.write(context)
                continue
            context = a[:-1]+"\t"+res[0]+"\n";
            f_out.write(context)

        
def readgb():
    import pandas as pd
    f = open("./US/US.txt", encoding="utf8")
    df = pd.DataFrame(pd.read_csv(f, sep="\t"))
    return df


def main():
    Translation = translation("./rule")
    f2 = open("./US/2wordstransbymose.txt", "a", encoding='utf-8')
    f3 = open("./US/3wordstransbymose.txt", "a", encoding='utf-8')
    f4 = open("./US/multiwordstransbymose.txt", "a", encoding='utf-8')
    errr = open("aa", "a", encoding='utf-8')
    df = readgb()
     # len(open("./英国测试/transbymose.txt","r",encoding='utf-8').readlines())
    for line in df["name"]:
        phrase = line
        try:
            a = Translation.phrasetrans(phrase)
            print(a)
            if len(phrase.rsplit())>3:
                f = f4
            elif len(phrase.rsplit())>2:
                f = f4
            else:
                f = f2
            f.write(str(phrase + "\t" + a + "\n"))
            f.flush()
            i = i + 1
            if i % 100 == 0:
                print(i)
        except:
            errr.write(str(phrase + "\n"))
            errr.flush()


def Wordtest():
    Translation = translation("./rule")
    aa, _ ,log= Translation.phrasetrans("Saint Margaret's at Cliffe")
    print(aa)
    print(_) # 音译 意译tag  未译 -1 音 0 照搬 1  意 2
    print(log)

def communicate2bashtest():
    s = subprocess.Popen([r".\PowerShellCmd\Mosebyword.bat", "mosesdecoder/bin/moses -f  mert-work/moses.ini"], stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
    stdoutdata, _ = s.communicate(input="a b a n a n".encode("utf-8"))

def filetranstest():
    Translation = translation("./rule")
    Translation.filetrans("sample.txt")

if __name__ == '__main__':
    filetranstest()
