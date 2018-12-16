import logging
import pickle

import jieba_fast
import numpy as np
import pandas as pd
from collections import defaultdict
from utils import nlp_zero
from utils.RuleDict import PrepTranlstionRuleDict
from utils.webtrans import translateBybaidu, translateBygoogle

logging.basicConfig(level = logging.INFO, format = '%(asctime)s - %(name)s - %(message)s')


def readfile(filepath):
    f = open(filepath,encoding="utf8")
    df = pd.DataFrame(pd.read_csv(f,sep=","))
    return df




def templates_generate(sents_list,filepath,language,min_proba=1e-4,filtering=False):
    f = nlp_zero.Template_Finder(str.rsplit, window=9,min_proba=min_proba)
    f.train(sents_list,filtering=filtering)
    f.find(sents_list,filtering=filtering)

    templates = pd.Series(f.templates).sort_values(ascending=filtering)
    idx = [i for i in templates.index if len(i.words)>1]
    templates = templates[idx] # 筛选出非平凡的模版

    f = open(filepath+"/"+language+"templates_asc","wb")
    pickle.dump(templates,f)
    w =open(filepath+"/"+language+"templates_asc","w",encoding="utf8")
    for i in idx:
        print((i,templates[i]), file=w)

def loadParser_trandict(filepath):
    template_tran_hashdict =  defaultdict(str)
    with open(filepath, "r", encoding="utf8" ) as Templates_file:
                for i,Template in enumerate(Templates_file):
                    if i == 322:
                        aaa =1
                    if Template == "\n":
                        continue
                    _, num, word = nlp_zero.parseTemplate(Template)

                    template_tran_hashdict[str(nlp_zero.Template(word))]=(_,num)
    trie = nlp_zero.XTrie()
    trie.LoadTemplatesfromFile(filepath)#"./templates/template_tran.txt")
    p = nlp_zero.Parser(trie, template_tran_hashdict,str.rsplit)
    return p,template_tran_hashdict




def fprint(r,file,template_tran_hashdict,tranlist):
    print(r.sent_tran(tranlist=tranlist)[0],file=file)

class TemplateTranslation(object):
    templates = None
    translate_fn = None

    def __init__(self,templates,translate_fn=translateBybaidu):
        if isinstance(templates[0],nlp_zero.Template()):
            self.templates = templates
        self.translate_fn = translate_fn


    def checkxyz(self,tran, template):
        """
        确认翻译结果是否有占位符
        """
        num = len(template.Nonepos)
        placeholder = ["X","Y","Z","M","N",]
        for i in range(num):
            if placeholder[i] not in tran:
                return False
        return True


    def split_tran(self,template):
        num = len(template.Nonepos)
        placeholder = ["X","Y","Z","M","N"]
        stc = template.str_no_none()
        tran = translateBybaidu(stc)
        seg = list(jieba_fast.cut(tran))
        for i in range(num):
            seg.insert(template.Nonepos[i],"["+placeholder[i]+"]")
        return " ".join(seg)


    def fprint(self,file, template, tran):
            file.write(str((str(template),tran)))
            file.write("\n")
            file.flush()


    def template_tran(self,savefile):
        """
        获取模板的翻译，
        并以('[X] isles', ('[X]岛', 5))的形式保存
        """
        ttt = open(savefile+".txt","w",encoding="utf8")
        tran_res = []
        num = 0
        for i in self.templates.index:
            if len(i.str_no_none())<2:
                continue
            tran = self.get_trans(i)
            tran_res.append((str(i),tran))
            #fprint(ttt, i, tran)
            num+=1
        print(num)
        tt = open(savefile+".pkl","wb")
        pickle.dump(tran_res,tt)

    def template_tranUpdate(self,savefile,min_num=5):
        """
        舍去频数小的模板
        """
        tran_res = {}
        tran_list = []
        ttt = open(savefile+".txt","r",encoding="utf8")
        for i in ttt:
            str_,(tran,num_ )= eval(i)
            if num_<min_num:
                continue
            tran_res[str_] = (tran,num_)
            tran_list.append((str_,(tran,num_ )))
            num+=1
        ttt.close()
        ttt = open(savefile+".txt","w",encoding="utf8")
        for line in tran_list:
            ttt.write(str(line)+"\n")
        tt = open(savefile+".pkl","wb")
        pickle.dump(tran_res,tt)


    def get_trans(self,templates):
        tran = self.translate_fn(str(templates))
        tran = tran.upper()
        if not self.checkxyz(tran, templates):
            #print(tran)
            tran = self.split_tran(templates)
            #print(tran)
        return tran


def main():
    p,template_tran_hashdict = loadParser_trandict("./templates/template_tran.txt")
    res = p.parse("aaaaaaaaaa stack bbbbbbbbbb grove".lower(),10)
    for r in res:
        r[0].get_templatestrans(template_tran_hashdict)
        print(str(r[0].template) in template_tran_hashdict)
        print(str(r[0].line())+"  "+str(r[1]))
        a = r[0].toWordlist()
        print(str(r[0].template)+r[0].template.trans_res)
        print(r[0].sent_tran()+"\n")

if __name__ == '__main__':
    main()