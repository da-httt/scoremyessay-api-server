import enchant 
import re 

def spellCheck(text):
    #choose the dictionary 
    d = enchant.Dict("en_US")
    
    #Store number of misspelt words 
    numIncorrect = 0
    
    #Store misspelt words in dictionary
    misspelt = []
    
    #split text into words 
    wordList = re.findall(r"\w+", text)
    
    #checking misspelt words 
    for index, word in enumerate(wordList):
        if d.check(word) == False:
            misspelt.append(
                {"index":index, 
                 "word": word,
                 "suggested_word": d.suggest(word)[0]}
            )
            numIncorrect += 1
            
    
    return numIncorrect, misspelt

if __name__ == "__main__":
    
    text = '''Social networking Vitnam websites like Faxcebook, Twitter and Instagram have become an important part of our everyday life. However, it is argued that these sites have a devastating effect on the community and the individuals. I strongly agree with the thought that social websites have a profound negative effect. 
To begin with, social networking sites have started hurting relationships. In the present world, people spend a lot of time online. Hence, they do not have time to visit their friends or relatives. As a result, relationships have become shallow. For example, in the earlier days, individuals used to have get-togethers at least once a month, but nowadays most of the people do not even know many of their relatives. Consequently, there are no close helpful relationships in this era.Addiction is another drawback of social networks which leads to failure in almost every field. Most of the people waste hours in front of computers or mobile phones chatting and posting on Facebook and Twitter and thus they fail to pay attention to their work. For instance, students do not perform their best in the exams or fail because they spend more time online instead of studying. As a result, social networking sites hinder the progress of the individual and also of the society. 
In conclusion, althoungh Facebook and such sites are beneficial to some extent, I strongly agree with the argument that they have more detrimental effect on both the local community and the people. It is hoped that users will realize this and learn to use such platforms more judiciously.'''
    numIncorrect, misspelt = spellCheck(text)
    
    print("Number of incorrect words: ", str(numIncorrect))
    print("Misspelt words: ")
    print(misspelt )