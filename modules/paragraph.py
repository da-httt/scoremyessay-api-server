from  nltk import tokenize 
import re 

def paragraph_to_sentences(para):
    sentences = tokenize.sent_tokenize(para)
    return sentences 

def getWordCount(para):
    wordList = re.findall(r'\w+', para)
    return len(wordList)

def getSentenceCount(para):
    sentences = tokenize.sent_tokenize(para)
    return len(sentences)

def getAvgSentenceLength(text):
	#split the essay into sentences
	sentList = nltk.sent_tokenize(text)

	sumSentLength = 0
	for sent in sentList:
		sumSentLength = sumSentLength + getWordCount(sent)

	#print float(sumSentLength)/len(sentList)
	return float(sumSentLength)/len(sentList)

