import re
try:
    from utils.RuleDict import PrepTranlstionRuleDict
except:
    from RuleDict import PrepTranlstionRuleDict  # 为了单独调试
from sqlite3 import connect
"""
try:
    conn = connect('../rule/instance_database.db')
except:
    conn = connect('./rule/instance_database.db')
SQL = '''SELECT * FROM "main"."instan" WHERE "英文词名" = '{}' '''
c = conn.cursor()
batch_size = 200"""


class Wordlist(list):
    '''
    地名词列表，用于标志翻译内容，是否翻译，翻译形式
    __init__(self, wordlist):
    :wordlist 可以是wordlist类，也可以是形如["a","b"]的list
    '''
    InstanceTpye = int(-1) # 实例类别 专名实例 1 通名实例 2  0 介词或冠词 -1 未定
    trans_level = 0
    try:
        conn = connect('../rule/instance_database.db',check_same_thread=False)
    except:
        conn = connect('./rule/instance_database.db',check_same_thread=False)
    SQL = '''SELECT * FROM "main"."instan" WHERE "英文词名" = '{}' '''
    c = conn.cursor()
    batch_size = 200

    def __repr__(self):
        return self.__str__()+"---"+" ".join([i.transContext for i in self])

    def __str__(self):
        return self.SourceContext

    def transContexts(self):
        return [i.transContext for i in self]

    def SourceContexts(self):
        return [i.SourceContext for i in self]

    def transTags(self):
        return [i.transTag for i in self]

    def __init__(self, wordlist):
        """
        :wordlist 可以是wordlist类，也可以是形如["a","b"]的list
        """
        list.__init__([])
        self.prep_tag = list()
        if isinstance(wordlist, Wordlist):
            self.prep_tag = wordlist.prep_tag
            self.extend([Word(i.SourceContext) for i in wordlist])
            for i, j in zip(self, wordlist):
                i.transContext = j.transContext
                i.transTag = j.transTag
        else:
            self.extend([Word(i) for i in wordlist])
            pos = 0
            for i, j in zip(self, wordlist):
                if j in PrepTranlstionRuleDict.keys():
                    self.prep_tag.append(pos)
                pos += 1
        self.updatewordidx()

    def updatewordidx(self,idx=0):
        for i in self:
            idx+=1
            if isinstance(i, Wordlist):
               idx= i.updatewordidx(idx-1)
            else:
                i.idx=idx
        return idx

    @property
    def transTag(self):
        """
        list的翻译tag规则：
        list中有词未翻即全未翻
        有意译全为意译
        ...
        """
        _transTags = self.transTags()
        if -1 in _transTags: # 未翻即全未翻
            return -1
        if 2 in _transTags:
            return 2  # 有意义 即全意义
        if 0 in _transTags:
            return 0
        if 1 in _transTags:
            return 1
        if _transTags == [0.5]:
            return 0.5
        return ValueError("transTag Error")

    @property
    def transContext(self):
        return "".join(self.transContexts()).replace(" ","")

    @property
    def SourceContext(self):
        return " ".join(self.SourceContexts())

    @property
    def length(self):
        return len(self)


    def CheckinInstance(self,tranTag = 0):
        '''检查短语中单词是否在实例库'''
        instan_idx = []
        for i,word in enumerate(self):
            SQL_inst = self.SQL.format(str(word.SourceContext))
            query_res =  self.c.execute(SQL_inst).fetchall()
            cn = ""
            for row in query_res:
                cn = row[3]
                if len(cn)>28:
                    cn =""
            if cn != "":
                instan_idx.append(i)
                word.transTag = tranTag
                word.transContext = cn
        return instan_idx



    def CheckinRule(self, RuleDict=dict(), tranTag = 2): # 专名实例 1 通名实例 2  0 介词或冠词 -1 未定
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
                continue  # 双词遍历，成果则去除所有缓存
            elif _[0] in RuleDict.keys():
                self[i-1].transContext = RuleDict[_[0]]
                self[i-1].transTag = tranTag
                _ = letter # 双词遍历，成果则去除第一个缓存
                continue
            else:
                if self[i].transTag == -1:
                    unkown.add(_[0])
                _ = letter  # 啥都没
        if _ in RuleDict.keys():  # 最后一个落单的变量
            self[i].transContext = RuleDict[_]
            self[i].transTag = tranTag
        else:
            unkown.add(_)
        if "" in unkown:
            unkown.remove("")
        return unkown

    def CheckSpecialChar(self):
        for i in range(self.length):
            if isinstance(self[i],Wordlist):
                continue
            if not self[i].SourceContext.isalpha():
                self[i].transContext = self[i].SourceContext
                self[i].transTag = 1

    def marge(self, startidx, endidx, method="word", sep=" "):
        """
        合并 从startidx到endidx
        method="word" 或 "wordlist" 表示合并的类
        sep  表示合并为word时单词的间隔
        对于word形时，需要保证翻译tag的相似性
        """
        if method == "word":
            def checktag(tag1, tag2):
                if abs(tag1 - tag2) < 2:
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
        if method == "wordlist":
            endidx = endidx + 1
            poplist = []
            for idx in range(startidx, endidx):
                a = self.pop(startidx)
                poplist.append(a)
            mergelist = Wordlist(poplist)
            self.insert(startidx, mergelist)



    def insert(self, idx, word):
        if  isinstance(word, Word):
            super().insert(idx, word)

        elif isinstance(word, Wordlist):
            super().insert(idx, word)
        else:
            raise TypeError("not Wordlist or Word")




class Word(str):
    SourceContext = ""
    transContext = ""
    trans_level = 0
    idx = 0
    transTag = int()
    """音译 意译tag  未译 -1   音 0  省译 0.5 照搬 1  意 2"""
    InstanceTpye = int(-1) # 实例类别 专名实例 1 通名实例 2  0 介词或冠词 -1 未定

    def __init__(self, word):
        if isinstance(word, Word):
            self.SourceContext = word.SourceContext
            self.transContext = word.transContext
            self.transTag = word.transTag
        else:
            self.SourceContext = word
            self.transContext = ""
            self.transTag = -1


    def __repr__(self):
        return str(self.SourceContext +" | " + str(self.transContext))


    def __len__(self):
        return len(self.SourceContext)

    def transContexts(self):
        return self.transContext

    def SourceContexts(self):
        return self.SourceContext





def main():
    wl = Wordlist("Frilford Heath aa bb cc A338".rsplit())
    wl.CheckinRule()
    wl.CheckSpecialChar()
    print(wl)
    al = Wordlist(wl)
    print(al)
    #al.marge(1,4)
    cl = Wordlist("Saint Margaret's at Cliffe".rsplit())
    word = Word("hhh")
    word.transContext = "ggg"
    word.transTag = 2
    cl.insert(-1,al)
    print(al)

def Wordtest():
    a = Word("a")
    b = Word("accccc")

def testinstance():
    from Modify import Modify
    Modify = Modify()
    cl = Wordlist(Modify.modifyphrase("Saint Margaret's at Cliffe").rsplit())
    cl.CheckinInstance()
    print(cl)



if __name__ == '__main__':
    main()