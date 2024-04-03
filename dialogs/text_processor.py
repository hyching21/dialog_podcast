import jieba

class TextProcessor:
    async def get_transcript(file):
        with open(file, 'r', encoding='utf-8') as f:
            text = f.read()
        return text

    async def get_stopword(file):
        stopword_list = []
        with open(file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                stopword_list.append(line)
        return stopword_list

        
    async def word_segmentation(text, needRemoveStopwords):
        seg_list = jieba.lcut(text)
        filtered_seg_list = []
        if needRemoveStopwords == True:
            stopword_list = TextProcessor.get_stopword("stopwords.txt")
            for word in seg_list:
                if word not in stopword_list :
                    if word != ' ':
                        filtered_seg_list.append(word)
            return filtered_seg_list
        else:
            return seg_list




