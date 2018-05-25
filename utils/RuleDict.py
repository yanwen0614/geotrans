from pickle import load
import os


__doc__ = '''modify的各种规则'''


PhraseRuleDict = {
            "'s": "",  
            "-": "",
            "'": " ",
            "!": "",
            "&":"and"
        }

IPARuleDict = {
        "tr": "t r ",
        "iə": "i ə ",
        "ɔi": "ɔ i ",
        "uə": "ə",
        "ɒ": "ɔ",
        "g": "ɡ",
        "dr ": "d r ",
        "a ": "ɑː ",
        "ɑ ": "ɑː ",
}

PrepReplaceRuleDict = {
        "and": "-",   # 4141
        "with": "-",  # 4132
}

PrepTranlstionRuleDict = {
        "on": "中的",   
        "at":"中的",
        "by": "的的",
        "in": "内的",
        "upon": "上的",
        "near": "边的",
        "of":"",

}

ArtRuleDict = {   # 412
        "a": "",
        "an": "",
        "the": "",
}

PreDict = {
        "st": "圣",
}




class MappingRule():

    IPA2CN = dict()
    EN2CN_Name = dict()
    EN2CN_Place = dict()
    EN2CN_Prefix = dict()
    EN2CN_Suffix = dict()

    def __init__(self, RuleFolderPath = "./rule"):
        self.IPA2CN = load(open(os.sep.join((RuleFolderPath, "英语音译对应表")), "rb"))
        self.EN2CN_Name = load(open(os.sep.join((RuleFolderPath, "英语地名中常用人名译写表pkl")), "rb"))
        self.EN2CN_Place = load(open(os.sep.join((RuleFolderPath, "英语地名常用通名和常用词汇译写表pkl")), "rb"))
        self.EN2CN_Prefix = load(open(os.sep.join((RuleFolderPath, "英语地名常用构词成分译写表前缀pkl")), "rb"))
        self.EN2CN_Suffix = load(open(os.sep.join((RuleFolderPath, "英语地名常用构词成分译写表后缀pkl")), "rb"))
