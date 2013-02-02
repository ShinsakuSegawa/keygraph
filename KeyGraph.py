#! python/keygraph/KeyGraph.py
# -*- coding: utf-8 -*-
import sys
import MeCab
import codecs
import re, pprint
import itertools
import time
import unicodedata
import os 
 
sys.stdout = codecs.getwriter('utf_8')(sys.stdout)
sys.stdin = codecs.getreader('utf_8')(sys.stdin)

def pp(obj):
    pp = pprint.PrettyPrinter(indent=4, width=160)
    str = pp.pformat(obj)
    return re.sub(r"\\u([0-9a-f]{4})", lambda x: unichr(int("0x"+x.group(1),16)),str)

  
M = 30

print 'start'

def readFiles():
    f_list = os.listdir('/Users/SS/python/keygraph/txt_files/')
    files = []
    for f in f_list:
        files.append(f.replace(".txt", ""))

    for f in files:
        print f

    return files


#ノイズの削除
def delNoise(text):
#   ノイズファイルの読み込み
    noise_list=[]
    for line in codecs.open('./noise/noise.txt', 'r', 'utf-8'):
        noise_list.append(line[:-1].split("\n"))	

#   ノイズ削除
    for i in range(len(noise_list)-1):
        noise =  noise_list[i]
        text = text.replace(noise[0], u'')
    return text 
 
#センテンス（文）のlist作成
def creSentence(text):
    s_cha = u'。'
#	    cat = re.split(ur"", text)
    sents = []
    sents = text.strip(s_cha).split(s_cha)
    return sents

#名詞だけを取得してリストにいれる　リストを返す 数字抜き
def pyMecab(s):
    tagger = MeCab.Tagger('-Ochasen')
    node = tagger.parseToNode(s.encode('utf-8'))
    nouns = []
    while node:
#		    めかぶの名詞のidが38から60なんだよね　数字id=48抜き
        if node.posid >= 38 and node.posid <= 67 and not(node.posid == 49):
            if isValid(node.surface.decode('utf-8')) == True:
                nouns.append(node.surface.decode('utf-8'))
        node = node.next
    return nouns


def isValid(word):
    alldigit = re.compile(ur"^[0-9]+$")
    """wordが登録対象の単語のときTrueを返す"""
# 	    1文字の単語は登録しない
    if len(word) == 1:
        return False
# 	    数字だけの単語は登録しない
    if alldigit.search(word) != None:
        return False
# 	    仮名2文字の単語は登録しない
    if len(word) == 2 and unicodedata.name(word[0])[0:8] == "HIRAGANA" and unicodedata.name(word[1])[0:8] == "HIRAGANA":
        return False
#       仮名、漢字、数字、英字以外の文字を含む単語は登録しない
    for c in word:
        if not (unicodedata.name(c)[0:8] == "HIRAGANA" or
               unicodedata.name(c)[0:8] == "KATAKANA" or
               unicodedata.name(c)[0:3] == "CJK" or
               unicodedata.name(c)[0:5] == "DIGIT" 
#               英語を削除しています　コメントをとれば英語も入ります． 
              ''' unicodedata.name(c)[0:5] == "LATIN"'''):
            return False
    return True
#   popで熟語のやつを消すぜー	
def pop(dic_p, dic_q):

    list_p = dic_p.items()
    list_p.sort(key=lambda a: a[1])
    list_q = dic_q.items()
    list_q.sort(key=lambda a: a[1])
     
    for kq,vq in list_q:
        for kp,vp in list_p:
#			含むかどうか確認
            if(kq.count(kp)>0):
#				print kp, di_comb_p[kp], kq, di_idiom_q[kq]
                if(dic_p.get(kp) <= dic_q.get(kq)):
                    if(dic_p.has_key(kp)):
                        #print kp, kq
                        dic_p.pop(kp)
                else:
                    if(dic_q.has_key(kq)):
                        #print kq, kp
                        dic_q.pop(kq)
            if(kp.count(kq)>0):
#				print kp, di_comb_p[kp], kq, di_idiom_q[kq]
                if(dic_p.get(kp) <= dic_q.get(kq)):
                    if(dic_p.has_key(kp)):
                        #print kp, kq
                        dic_p.pop(kp)
                else:
                    if(dic_q.has_key(kq)):
                        #print kq, kp
                        dic_q.pop(kq)
                         
                         
    list_p = dic_p.items()
    list_q = dic_q.items()
    list_idiom = list_p
    list_idiom.extend(list_q)
    list_p.sort(key=lambda a: a[1])

    return list_p


#[語(word):出現回数]の辞書を作る
def freqcount(tokens):
    result={}
#   単語の出現でカウント(list内のカウント）
    for t in tokens:
        if result.has_key(t):
            result[t] += 1
        else:
            result[t] = 1
    return result	
 
#リスト['word']['sentence　インデックス']=出現回数　を返す関数
def calwfs(words, sents):
    wfs = {} 
    for w in words:
        for s in sents:
            if w in wfs:
                wfs[w][s] = s.count(w)
            else:
                wfs[w] = {}
                wfs[w][s] = s.count(w) 

#	for w,n in words:
#		for s in range(len(sents)):
#			print wfs[w][s]	

    return wfs	
 
#共起度coを計算する
def calCo(hf,sents):
    co = {} 
    for hf1 in hf:
        co[hf1] = {} #初期化
        for hf2  in hf[hf.index(hf1)+1:]:
            co[hf1][hf2] = 0 #初期化だよ 
            for s in sents:
                co[hf1][hf2] += s.count(hf1) * s.count(hf2)
                 
#	listにしています	
    co_list = [] 
    for x in co.keys():
        for y in co[x].keys():
            co_list.append([x,y,co[x][y]])
    
    co_list.sort(key=lambda a: a[2])

    return co_list 
 
 
#linkを張る
def link(base):
    base_set = flatten(base)
    base_set = set(base_set)
         
    print list(base_set)
    return list(base_set)
     
#リストの平坦化 
def flatten(x, isflat=lambda x:not isinstance(x, list)):
    if isflat(x):
        yield x
    else:
        for item in x:
            for i in flatten(item, isflat):
                yield i
                            
#key値の計算
def key(words, wfs, base, sents):
#	keyは辞書型　key = {w:key値}	
    key = {}
     
    Fg = fg(words, wfs, base, sents)

    for w in words:
        tmp = 1.0
        tmp_count = 0
        for g in base:
            tmp *= (1-(fwg(w,wfs,g,sents)*(1.0)/Fg[g])) 
        key[w] = 1.0-tmp 
        print 1.0-tmp, w 
         
    return key		

#f(w,g)計算
def fwg(w,wfs,g,sents):	
    gws = 0
    fwg = 0
    for s in sents:
#		|g-w|sの計算  gs = wfs[g][s] ws = ws[w][s]
        if g.find(w) >= 0:# w ∈ g
#			|g|sの計算
            gws = wfs[g][s] - wfs[w][s]
        else:# w not ∈ g
            gws = wfs[g][s]
        fwg += wfs[w][s]*gws
    return fwg

#F(g)の計算
def fg(words, wfs, base, sents):
    fg = {}
    for g in base:
        fg[g] = 0
        for s in sents:
            for w in words:
                if s.find(w) >= 0:
                    if g.find(w) >= 0:# w ∈ g
                        fg[g] += wfs[g][s] - wfs[w][s]
                    else:# w not ∈ g
                        fg[g] += wfs[g][s] 
    return fg


def C(hk, base, sents):
    c = {}
    for k in hk:
        c[k] = {}
        for b in base:
            c[k][b] = 0
            for s in sents:
                    c[k][b] += s.count(k) * s.count(b)
    
          
#	listにしています	
    c_list = [] 
    for x in c.keys():
        for y in c[x].keys():
            c_list.append([x,y,c[x][y]])
    
    c_list.sort(key=lambda a: a[2])

    return c_list 
  
def draw(base, G_C,fname):
    fout = codecs.open("./dot/" + fname + ".dot","w","utf-8")
    fout.write('graph keygraph {\n')
    fout.write('graph [size="10,10"]\n')
    for i,j in base:
       fout.write(i + '--' + j +'\n')
    for i,j in G_C:
       fout.write(i + '--' + j + '[style="dotted"]\n')
    fout.write('}')
     
    fout.close()

#隣接リストを作ったけど微妙だね． 
def adjacency_dic(base, G_C, fname):
    a_dic = {}
     
    for i,j in base:
        if a_dic.has_key(i):
            a_dic[i].append([j,'base'])
        else:
            a_dic[i] = [[j,'base']] 
        if a_dic.has_key(j):
            a_dic[j].append([i,'base'])
        else:
            a_dic[j] = [[i,'base']] 
    
    for i,j in G_C:
        if a_dic.has_key(i):
            a_dic[i].append([j,'key'])
        else:
            a_dic[i] = [[j,'key']] 
        if a_dic.has_key(j):
            a_dic[j].append([i,'key'])
        else:
            a_dic[j] = [[i,'key']] 


    fout = codecs.open("./adjacency_list/" + fname + ".txt","w","utf-8")
    fout.write(pp(a_dic.items()))
    fout.close()

         
         
        
#-----------Main----------------
if __name__ == "__main__":
    stime = time.time() 
#   コンソールからファイル名を読み込む 
    argvs = sys.argv
    argc = len(argvs)
    if(argc != 2):
        print 'Usage: #python %s filename' % argvs[0]
        quit()
         
    print pp(argvs)
    fname = argvs[1]
    
    
    f = codecs.open('./txt_files/' + argvs[1] + '.txt', 'r', 'utf-8')
     
    text = f.read()
    f.close()

#	ノイズの削除
    nc_text = delNoise(text)
     
#	センテンスリストの作成
    sents = creSentence(nc_text)

#	形態素解析
    tokens = pyMecab(nc_text) 
       
#	単語-出現度の辞書作成	
    freq_dict = freqcount(tokens)
    
    words_freq = sorted(freq_dict.items(), key=lambda x:x[1])
     
    words_freq = pop(dict(words_freq), dict(words_freq)) 
     
    words = [w for w,z in words_freq]
     
#	リスト[words][センテンス番号] = 出現回数のリストwfs
    wfs = calwfs(words, sents)

#	HighFreqを決める
    hf = [w for w,f in words_freq[-30:]]

#   HighFreqの共起度を計算する 返り値リスト[wi,wj,co]
    co = calCo(hf,sents)
     
    del words[-30:]
     
    base = [[i,j] for i,j,c in co[-30:]]  

        
    #baseに入っているノードを返す      
    G_base = link(base)   
     
    print G_base 
    
#	keyの計算  
    key = key(words, wfs, G_base, sents)
 
#	high_keyの計算
    high_key = sorted(key.items(), key=lambda x:x[1])
    high_key = high_key[-12:]
    
    high_key = [k for k,f in high_key]
     

#	c(wi,wj)の計算 [hk, base, スコア]が返り値
    C = C(high_key, G_base, sents)	
     
    C.sort(key=lambda x:x[2])
     
    G_C = [[i,j] for i,j,c in C[-12:]]  
     
    for i,j in base:
        print i,j
    
    for x,y in G_C:
        print x,y
    
    draw(base, G_C, fname)

    adjacency_dic(base, G_C, fname)
         
    etime = time.time()
 

print etime - stime	

