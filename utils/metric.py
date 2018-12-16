from math import e


normallist = [1,0.728535737,0.765945575,0.795861456687676]

def calcScoreAndtran(translist,parse_result_sentTree,SentTree_Score,max_log_p):
    sqr_para = 15
    sigmod_para = 5
    Sent_len = len(translist)
    BaseAccuracy=0.9
    mdnum_penalty = 1
    Sent_len_penalty = 1
    translit_penalty = 0.2
    word = set() # 音译单词索引集合
    tran, _, un = parse_result_sentTree.sent_tran(tranlist=translist) # 翻译结果 ， ，单独的词列表
    #tran, _, un = parse_result_sentTree.sent_tran(tranlist=[  "$$$$$" for i in range(Sent_len)])
    if un == -1:
        return tran, ("调用百度", 0.5,0.5,0.5,0.5),(0,0,0)
    for i in un:
        if translist[i].transTag == 0:
            word.add(i)
    word2instan = word.intersection(set(translist.instan_idx))
    word_len = len(word)
    mdnum = parse_result_sentTree.getModelnum
    if word_len==0:
        translit_acc = 1
    else:
        translit_acc = 1*(BaseAccuracy**(word_len-len(word2instan))) if word_len-len(word2instan)<4 else BaseAccuracy**((e**(word_len-len(word2instan)-3))*word_len-len(word2instan))
    if mdnum > 3:
        mdnum_penalty = e**(1-mdnum/3)
    """
    if Sent_len>3:
        Sent_len_penalty = e**(1-Sent_len/3)
    """
    if mdnum == 0:
        sqr_template_acc=0
        sigmod_template_acc=0
        sqr_acc = translit_acc
        sigmod_acc = translit_acc
    else:
        sqr_template_acc = mdnum_penalty*(e**(SentTree_Score/mdnum-max_log_p))**(1/sqr_para)
        sigmod_template_acc = mdnum_penalty*sigmod(e**(SentTree_Score/mdnum-max_log_p)*1000-sigmod_para )
        sqr_acc = Sent_len_penalty*(sqr_template_acc*(Sent_len - word_len) + translit_penalty*translit_acc*word_len) / (Sent_len-(1-translit_penalty)*word_len)
        sigmod_acc= Sent_len_penalty*(sigmod_template_acc*(Sent_len-word_len)+translit_penalty*translit_acc*word_len)/  (Sent_len-(1-translit_penalty)*word_len)#-(1-translit_penalty)*word_len)
    n_factor = normallist[3]
    if Sent_len<4 and mdnum>0:
        n_factor = normallist[Sent_len-1]
    sqr_acc = sqr_acc/n_factor if sqr_acc/n_factor<1 else sqr_acc
    return tran,(translit_acc, sqr_template_acc,sigmod_template_acc,sqr_acc,sigmod_acc),(SentTree_Score, mdnum, word_len,Sent_len)

def sigmod(x,a=1,b=1):
    return a/(b+e**(-x))