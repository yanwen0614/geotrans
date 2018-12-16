try:
    from utils.wordlist import Wordlist, Word
    from utils.RuleDict import *
except:
    from wordlist import Wordlist, Word
    from RuleDict import *
import re
import nltk.stem as ns


class SupportFunction(object):
    """
    modify类的辅助函数
    """

    def Preptranslation(self):
        raise NotImplementedError

    def trans_mode(self,word):
        """
        判断翻译模式、
        0 全音译
        1  省译加顺序
        2  省译加倒序
        3  意译加倒序
        暂时用翻译模式做判断，之后改为词语/词组的种类
        """
        if isinstance(word, Word) or isinstance(word, Wordlist):
            if word.transTag == 2:
                self.Preptranslation = self.Preptranslation_order_ignorePrep
                return 1
            elif word.transTag == 0:
                self.Preptranslation = self.Preptranslation_reverse_order_ignorePrep
                return 2
            elif word.transTag == 3:
                self.Preptranslation = self.Preptranslation_reverse_order_notignorePrep
                return 3
            else:
                self.Preptranslation = self.Preptranslation_all_translitation
                return 0
        else:
            raise TypeError("Not Wordlist.Word")

    def Preptranslation_reverse_order_ignorePrep(self, wordlist, idx):
        return self.Preptranslation_reverse_order(wordlist, idx, True)

    def Preptranslation_reverse_order_notignorePrep(self,wordlist, idx):
        return self.Preptranslation_reverse_order(wordlist, idx, False)

    def Preptranslation_reverse_order(self, wordlist, idx, ignorePrep):
        """
        介词翻译修正中词语倒序
        """
        pre = wordlist[idx + 1:]  # 介词后内容
        wordlist_modify = Wordlist([])
        wordlist_modify.extend(pre)
        wordlist_modify.append(wordlist[idx])
        wordlist_modify.extend(wordlist[:idx]) # 倒序
        idx = len(pre)
        if ignorePrep:
            wordlist_modify[idx].transTag = 0.5 # 省译
        else:
            wordlist_modify[idx].transContext = PrepTranlstionRuleDict[wordlist_modify[idx]]
            wordlist_modify[idx].transTag = 2 # 意
        return wordlist_modify



    def Preptranslation_order_ignorePrep(self,wordlist, idx):
        """
        介词翻译修正中词语省译加顺序
        """
        wordlist[idx].transTag = 0.5
        return wordlist


    def Preptranslation_all_translitation(self,wordlist):
        pass

class Modify(object):
    '''
    用于wordlist的各种修正
    '''
    RuleMapping = MappingRule()
    PhraseRuledict = {}
    IPARuledict = {}
    ConjReplaceRuleDict = {}

    def __init__(self,rulepath = "./rule/adv"):
        self.PhraseRuledict = PhraseRuleDict  # 短语符号的。。。
        self.IPARuledict = IPARuleDict  # 为符合标准的音标调整
        self.ConjReplaceRuleDict = ConjReplaceRuleDict  # 连词替换
        self.PrepTranlstionRuleDict = PrepTranlstionRuleDict  # 介词意译
        f = open(rulepath, encoding="utf8")
        self.advlist = [l.rsplit()[0] for l in f.readlines()]  # 形容词表

    def phraseCleaning(self,phrase):
        return re.sub("[^0-9a-zA-Z'&]+"," ",phrase)

    def modifyphrase(self, phrase):
        '''
        针对特殊符号
        "'s": "s",
        "-": " ",
        "'": "",
        "!": "",
        "&":"and"
        '''
        phrase = str(phrase.lower())
        for k, v in sorted(self.PhraseRuledict.items(),reverse=True):
            phrase = phrase.replace(k, v)
        return self.phraseCleaning(phrase)

    def IPAmodify(self, ipastr):
        for k, v in self.IPARuledict.items():
            ipastr = re.sub(k, v, ipastr)
        return ipastr

    def _ArtModifyWordlist(self, wordlist):
        '''冠词修正'''
        if not isinstance(wordlist, Wordlist):
            raise TypeError("Not Wordlist")
        # wordlist = Wordlist(wordlist) 用来补全的
        # 首位冠词消去
        if wordlist[0].SourceContext in ArtRuleDict.keys():
            # wordlist[0].SourceContext = " "
            wordlist[0].transTag = 0.5
        return wordlist

    def _ConjModifyWordlist(self, wordlist):

        # wordlist = Wordlist(wordlist) 用来补全的

        for word in wordlist:
            for k,v in self.ConjReplaceRuleDict.items():
                if word.SourceContext == k:
                    word.transContext = v
                    word.transTag = 0.5 # 省译
        return wordlist



    def _Preptranslation(self, wordlist):
        '''
        介词意译
        修正原理：判断介词后是否为通名/或已有的专名实例 、
                是 则顺序变化
        '''
        spt = SupportFunction()
        tagwords = self.PrepTranlstionRuleDict.keys()
        SC = wordlist.SourceContexts()
        for _ in tagwords:
            if _ in SC:  # 源文中是否有介词
                idx = SC.index(_)
                if _ == "of":
                    return spt.Preptranslation_reverse_order_ignorePrep(wordlist, idx)
                if SC[idx+1] == "the" or SC[idx+1] == "a" or SC[idx+1] == "an": # 判断是否有冠词
                    trans_mode_tag = spt.trans_mode(wordlist[idx+2]) # 有冠词
                    wordlist[idx+1].transTag = 0.5
                else:
                    trans_mode_tag = spt.trans_mode(wordlist[idx+1]) # 无冠词
                return spt.Preptranslation(wordlist, idx)
        return wordlist

    def ModifyWordlistBf(self, wordlist):
        '''
        翻译前修正
        包括 冠词修正、连词修正、介词修正
        '''
        wordlist = self._ArtModifyWordlist(wordlist)
        wordlist = self._ConjModifyWordlist(wordlist)
        #wordlist = self._Preptranslation(wordlist)
        return wordlist

    def NoPrepOrdermodify(self, wordlist):
        '''无介词条件下词序更换'''
        poplist = []
        # 判断是否有介词
        if wordlist.prep_tag != []:
            return wordlist
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
        '''
        翻译后修正
        包括 无介词条件下词序更换 音译结果过长合并
        '''
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
            if trasnslitlist==[]:
                return wordlist
            for word_idx in trasns(trasnslitlist):
                length = 0
                for idx in word_idx:
                    length = length + len(wordlist[idx].transContext)
                if length >= 8:
                    wordlist.marge(word_idx[0], word_idx[-1], "-")
            return wordlist
        else:
            raise TypeError("Not Wordlist")



def main():
    pp = Modify(rulepath = "./rule/adv")
    a = pp._Preptranslation(Wordlist("Stow on the Wold".rsplit()))
    print(a.transContext())
    print(a.transTag())
    print(a.SourceContext())

if __name__ == '__main__':
    main()
