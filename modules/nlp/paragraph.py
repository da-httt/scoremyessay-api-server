from  nltk import tokenize 


def paragraph_to_sentences(para):
    sentences = tokenize.sent_tokenize(para)
    return sentences 


