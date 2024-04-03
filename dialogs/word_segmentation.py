import jieba

def get_transcript(file):
    with open(file, 'r', encoding='utf-8') as f:
        text = f.read()
    return text

def get_stopword(file):
    stopword_list = []
    with open(file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            stopword_list.append(line)
    return stopword_list

       
def word_segmentation(text, needRemoveStopwords):
    seg_list = jieba.lcut(text)
    filtered_seg_list = []
    if needRemoveStopwords == True:
        stopword_list = get_stopword("stopwords.txt")
        for word in seg_list:
            if word not in stopword_list :
                if word != ' ':
                    filtered_seg_list.append(word)
        return filtered_seg_list
    else:
        return seg_list


# textfile ='【好味小姐】[20230626] EP167 我小時候的第一個記憶....txt'
# text = get_transcript(textfile)
# text2 = ['從小就覺得脆脆的哥哥比較聰明','從不想生小孩到接受生小孩','會不會對彼此的伴侶產生情愫','如果和同事在公司狹路相逢，要怎麼給反應、打招呼','家裡臭臭的就把阿寶跟秋葵抓過來聞']
# for i in range(5):
#     word_segmentation(text2[i], False)
#     word_segmentation(text2[i], True)

