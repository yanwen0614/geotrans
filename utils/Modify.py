try:
    from utils.wordlist import Wordlist
    from utils.RuleDict import *
except:
    from wordlist import Wordlist
    from RuleDict import *


class Modify(object):
    '''
    用于wordlist的各种修正
    '''
    RuleMapping = MappingRule()
    PhraseRuledict = {}
    IPARuledict = {}
    PrepReplaceRuledict = {}

    def __init__(self,rulepath = "./rule/adv"):
        self.PhraseRuledict = PhraseRuleDict
        self.IPARuledict = IPARuleDict
        self.PrepReplaceRuledict = PrepReplaceRuleDict
        f = open(rulepath, encoding="utf8")
        self.advlist = [l.rsplit()[0] for l in f.readlines()]

    def modifyphrase(self, phrase):
        '''针对特殊符号'''
        phrase = str(phrase).lower()
        for k, v in self.PhraseRuledict.items():
            phrase = phrase.replace(k, v)
        return phrase
    
    def IPAmodify(self, ipastr):
        for k, v in self.IPARuledict.items():
            ipastr = ipastr.replace(k, v)
        return ipastr

    def ArtModifyWordlist(self, wordlist):
        '''冠词修正'''
        if not isinstance(wordlist, Wordlist):
            raise TypeError("Not Wordlist")
        # wordlist = Wordlist(wordlist) 用来补全的
        if wordlist[0].SourceContext in ArtRuleDict.keys():
            wordlist = Wordlist(wordlist[1:])
        return wordlist

    def PrepModifyWordlist(self, wordlist):
        '''介词修正'''
        if not isinstance(wordlist, Wordlist):
            raise TypeError("Not Wordlist")
        # wordlist = Wordlist(wordlist) 用来补全的
        for word in wordlist:
            for k, v in self.PrepReplaceRuledict.items():
                if word.SourceContext == k:
                    word.transContext = v
                    word.transTag = 1
        return wordlist

    def ModifyWordlistBf(self, wordlist):
        '''翻译前修正'''
        wordlist = self.ArtModifyWordlist(wordlist)
        wordlist = self.PrepModifyWordlist(wordlist)
        wordlist = self.Preptranslation(wordlist)
        return wordlist

    def NoPrepOrdermodify(self, wordlist):
        '''无介词条件下词序更换'''
        poplist = []
        # wordlist = Wordlist(wordlist) 用来补全的
        for i in range(wordlist.length):
            if wordlist[i].SourceContext in self.RuleMapping.EN2CN_Place and wordlist[i].SourceContext not in self.advlist:
                poplist.append(i)
        t = 0
        for i in poplist:
            temp = wordlist.pop(i - t)
            wordlist.append(temp)
            t += 1
        return wordlist

    def ModifyWordlistAf(self, wordlist):
        '''翻译后修正'''
        wordlist = self.NoPrepOrdermodify(wordlist)
        wordlist = self.margetrasnslit(wordlist)
        return wordlist

    def margetrasnslit(self, wordlist):

        def trasns(tlist):
            temp = [tlist[0]]
            tempi = tlist[0]
            for i in tlist[1:]:
                if i - tempi != 1:
                    yield temp
                    temp = []
                tempi = i
                temp.append(i)
            yield temp

        trasnslitlist = []
        if isinstance(wordlist, Wordlist):
            for i in range(wordlist.length):
                if wordlist[i].transTag in (0,):
                    trasnslitlist.append(i)
            for word_idx in trasns(trasnslitlist):
                length = 0
                for idx in word_idx:
                    length = length + len(wordlist[idx].transContext)
                if length >= 8:
                    wordlist.marge(word_idx[0], word_idx[-1], "-")
            return wordlist
        else:
            raise TypeError("Not Wordlist")

    def Preptranslation(self, wordlist):
        tagwords = PrepTranlstionRuleDict.keys()
        SC = wordlist.SourceContext()
        for _ in tagwords:
            if _ in SC:
                idx = SC.index(_)
                pre = SC[idx + 1:]
                if "the" == pre[0]:
                    pre = pre[1:]
                wordlist_modify = Wordlist(pre+[SC[idx]]+SC[:idx])
                idx = len(pre)
                wordlist_modify[idx].transTag = 2 # 意
                wordlist_modify[idx].transContext = PrepTranlstionRuleDict[_]
                return wordlist_modify
        return wordlist

def main():
    pp = Modify(rulepath = "./rule/adv")
    a = pp.Preptranslation("Saint Nicholas at Wade".rsplit())
    print(a.transContext())
    print(a.transTag())
    print(a.SourceContext())

if __name__ == '__main__':
    main()