import re
import copy
try:
    from utils.RuleDict import MappingRule
except :
    from RuleDict import MappingRule


class Wordlist(list):
    '''
    地名词列表，用于标志翻译内容，是否翻译，翻译形式
    '''
    RuleMapping = MappingRule()
    length = int()

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return " ".join([i.SourceContext for i in self])

    def transContext(self):
        return [i.transContext for i in self]
    
    def SourceContext(self):
        return [i.SourceContext for i in self]
    
    def transTag(self):
        return [i.transTag for i in self]

    def __init__(self, wordlist):
        list.__init__([])
        if isinstance(wordlist, Wordlist):
            self.extend([Word(i.SourceContext) for i in wordlist])
            for i, j in zip(self, wordlist):
                i.transContext = j.transContext
                i.transTag = j.transTag
        else:
            self.extend([Word(i) for i in wordlist])
            for i, j in zip(self, wordlist):
                if isinstance(j, Word):
                    i.transContext = j.transContext
                    i.transTag = j.transTag
        self.length = len(wordlist)

    def CheckinRule(self, RuleDict=dict(), tranTag = 2):
        '''检查短语中单词是否在规则内'''
        unkown = set()
        _ = ""
        for letter, i in zip(self, range(self.length)):
            letter = letter.SourceContext
            _ = [_, letter]
            __ = " ".join(_)
            if __ in RuleDict.keys():
                self[i].transContext = RuleDict[__]
                self[i].transTag = tranTag
                self[i-1].transTag = tranTag
                _ = ""
                continue
            elif _[0] in RuleDict.keys():
                self[i-1].transContext = RuleDict[_[0]]
                self[i-1].transTag = tranTag
                _ = letter
                continue
            else:
                unkown.add(_[0])
                _ = letter
        if _ in RuleDict.keys():
            self[i].transContext = RuleDict[_]
            self[i].transTag = tranTag
        else:
            unkown.add(_)
        if "" in unkown:
            unkown.remove("")
        return unkown

    def CheckSpecialChar(self):
        for i in range(self.length):
            if not self[i].SourceContext.isalpha():
                self[i].transContext = self[i].SourceContext
                self[i].transTag = 1

    def marge(self, startidx, endidx, sep=" "):

        def checktag(tag1, tag2):
            if abs(tag1 - tag2) <= 1:
                return True
            return False

        endidx = endidx + 1
        transTag = self[startidx].transTag
        for idx in range(startidx, endidx):
            if not checktag(transTag, self[idx].transTag):
                raise ValueError
        temp = Word(" ".join([self[idx].SourceContext for idx in range(startidx, endidx)]))
        temp.transContext = sep.join([self[idx].transContext for idx in range(startidx, endidx)])
        temp.transTag = transTag
        for idx in range(startidx, endidx):
            self.pop(startidx)
        self.insert(startidx, temp)
        self.length = self.length - endidx + startidx
    


class Word(object):
    SourceContext = ""
    transContext = ""
    transTag = int()  # 音译 意译tag  未译 -1 音 0 照搬 1  意 2

    def __init__(self, word):
        self.SourceContext = word
        self.transContext = ""
        self.transTag = -1

    def __repr__(self):
        return str(self.SourceContext +"|" + self.transContext)
    
    def __len__(self):
        return len(self.SourceContext)




def main():
    wl = Wordlist("Frilford Heath A338".rsplit())
    wl.CheckinRule()
    wl.CheckSpecialChar()
    print(wl)
    al = Wordlist(wl)
    print(al)
    al.marge(1,2)

if __name__ == '__main__':
    main()