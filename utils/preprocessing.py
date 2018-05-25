import random

__doc__ = '''
用于英文英标mose训练语料的初始化
'''

class IPA(object):
    VowelAlphabet = ("ʌ", "i", "ɒ", "u", "ɔ", "o", "ə", "e", "æ", "ɑ", "a")
    doubleVowelAlphabet = ("ei", "ai", "ɔi", "iə", "ɛə", "uə", "au", "əu", "ɑː", "ɜː", "ɔː", "uː", "iː")
    consonantAlphabet = ("p", "b", "t", "d", "k", "ɡ", "g", "f", "v", "s", "z", "θ", "ð", "ʃ", "ʒ", "m", "n", "ŋ", "h", "l", "r", "j", "w")
    doubleconsonantAlphabet = ("tʃ", "dʒ", "tr", "dr", "ts", "dz")

    @staticmethod
    def SplitPhonetic(Phonetic=""):
        res = list()
        unkown = set()
        _ = ""
        for letter in Phonetic:
            _ += letter
            if len(_) != 2:
                continue
            if _ in IPA.doubleconsonantAlphabet or _ in IPA.doubleVowelAlphabet:
                res.append(_)
                _ = ""
                continue
            elif _[0] in IPA.consonantAlphabet or _[0] in IPA.VowelAlphabet:
                if _[0] == "g":
                    _[0] == "ɡ"
                res.append(_[0])
                _ = letter
                continue
            else:
                unkown.add(_[0])
                _ = letter
        if _ in IPA.consonantAlphabet or _ in IPA.VowelAlphabet:
            res.append(_)
        else:
            unkown.add(_)
        if "" in unkown:
            unkown.remove("")
        return res, unkown


class Tokenisation(object):
    '''
    mose语料初始化
    '''
    inputpath = ''

    def __init__(self, filepath):
        self.inputpath = filepath

    def tokenisationworld(self, word=""):
        res = list()
        for target_list in word:
            res.append(target_list)
        return " ".join(res)

    def tokenisation(self, outpath="."):
        inputf = open(self.inputpath, encoding="utf8")
        wordf = open(outpath + "/word", mode="w", encoding="utf8")
        wordftest = open(outpath + "/wordtest", mode="w", encoding="utf8")
        phoneticf = open(outpath + "/phonetic", mode="w", encoding="utf8")
        phoneticftest = open(outpath + "/phonetictest", mode="w", encoding="utf8")
        unkown = set()
        i = 0
        for line in inputf:
            linestr = line
            linestr = linestr.split(",")
            word = self.tokenisationworld(linestr[0])
            aa = IPA.SplitPhonetic(linestr[1][1:-2])
            Phonetic = " ".join(aa[0])
            if len(aa[1]) > 0:
                print(aa[1])
                unkown = unkown.union(aa[1])
            if random.random() < 0.05:
                wordftest.write(word + "\n")
                phoneticftest.write(Phonetic + "\n")
                wordftest.flush()
                phoneticftest.flush()
            wordf.write(word + "\n")
            phoneticf.write(Phonetic + "\n")
            wordf.flush()
            phoneticf.flush()
            i = i + 1
            # if (i % 1000) == 0 :
            #    print(i)
        print(" ".join(unkown))
