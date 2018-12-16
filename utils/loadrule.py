import pickle
import xlrd
import re

__doc__ = '''载入规则到pkl文件'''


class IPAMappingcn():
    vdict = dict()
    cdict = dict()
    mappdict = dict()

    def __init__(self, filepath="./rule/英语音译对应表.xlsx"):
        self.data = xlrd.open_workbook(filepath)

    def readIPAVtable(self):
        table_v = self.data.sheets()[0]
        _id = table_v.col_values(0)[1:]
        ipa = table_v.col_values(1)[1:]
        cn = table_v.col_values(2)[1:]
        self.vdict = {a: list() for a in _id}
        for a, b in zip(_id, ipa):
            self.vdict[a].append(b)
        for a, b in zip(ipa, cn):
            self.mappdict[a] = str(b).split("/")

    def readIPACtable(self):
        table_c = self.data.sheets()[1]
        _id = table_c.col_values(0)[1:]
        ipa = table_c.col_values(1)[1:]
        cn = table_c.col_values(2)[1:]
        self.cdict = {a: list() for a in _id}
        for a, b in zip(_id, ipa):
            self.cdict[a].append(b)
        for a, b in zip(ipa, cn):
            self.mappdict[a] = str(b).split("/")

    def readIPAMtable(self):
        table_c = self.data.sheets()[2]
        for i in range(1, 26):
            for j in range(1, 19):
                for a in self.cdict[i]:
                    for b in self.vdict[j]:
                        phonetic = a + b
                        self.mappdict[phonetic] = str(table_c.cell(j, i).value).split("/")

    def loaddictmapping(self):
        self.readIPACtable()
        self.readIPAVtable()
        self.readIPAMtable()
        data = open('./rule/英语音译对应表', mode='wb')
        pickle.dump(self.mappdict, data)
        data.close()


class RuleEN2CN(object):

    ruledict = dict()
    filename = ""

    def __init__(self, filename):
        self.filename = filename
        self.ruledict = dict()
        with open(filename, encoding="utf8") as target:
            self.df = target.readlines()

    def dump(self):
        data = open(self.filename+"pkl", mode='wb')
        pickle.dump(self.ruledict, data)
        data.close()


class NameRule(RuleEN2CN):

    def __init__(self):
        super().__init__("./rule/英语地名中常用人名译写表")

    def load(self):
        for indexs in self.df[1:]:
            line = indexs.rsplit()
            self.ruledict[line[0].lower()] = line[1]
            try:
                self.ruledict[line[2].lower()] = line[3]
            except:
                pass


class PalceRule(RuleEN2CN):

    def __init__(self):
        super().__init__("./rule/英语地名常用通名和常用词汇译写表")

    def load(self):
        for indexs in self.df[1:]:
            line = indexs.split("\t")
            self.ddd(line[0].lower(), line[1])
            try:
                self.ddd(line[2].lower(), line[3].strip())
            except:
                pass

    def ddd(self, key, value):
        value = value.split("、")[0]
        a = re.split("(\([a-zA-Z]\))", key)
        if len(a) == 1:
            self.ruledict[key] = value
        else:
            self.ruledict["".join([a[0], a[2]])] = value
            self.ruledict["".join([a[0], a[1][1], a[2]])] = value


class SubPalceRule(RuleEN2CN):

    def __init__(self):
        super().__init__("./rule/英语地名常用构词成分译写表")

    def load(self):
        for indexs in self.df[1:]:
            line = indexs.split("\t")
            self.ddd(line[0].lower(), line[1])
            try:
                self.ddd(line[2].lower(), line[3].strip())
            except :
                pass

    def ddd(self, key, value):
        value = value.split("、")[0]
        key, tag = self.checkkey(key)
        if not tag:
            return
        a = re.split("(\([a-zA-Z]\))", key)
        if len(a) == 1:
            self.ruledict[key] = value
        else:
            self.ruledict["".join([a[0], a[2]])] = value
            self.ruledict["".join([a[0], a[1][1], a[2]])] = value

    def checkkey(self, key):
        pass


class SuffixPalceRule(SubPalceRule):

    def __init__(self):
        super().__init__()
        self.filename = self.filename + "后缀"

    def checkkey(self, key):
        return key[1:], str(key).startswith("-")


class PrefixPalceRule(SubPalceRule):

    def __init__(self):
        super().__init__()
        self.filename = self.filename + "前缀"

    def checkkey(self, key):
        return key[:-1], str(key).endswith("-")

def loadrule(nr):
    nr.load()
    nr.dump()

def main():
    nr = SuffixPalceRule()
    loadrule(nr)
    nr = PrefixPalceRule()
    loadrule(nr)
    nr = PalceRule()
    loadrule(nr)
    nr = NameRule()
    loadrule(nr)
    aa = IPAMappingcn()
    aa.loaddictmapping()


if __name__ == '__main__':
    main()