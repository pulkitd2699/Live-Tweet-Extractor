import nltk
from nltk.corpus import state_union
from nltk.tokenize import PunktSentenceTokenizer

train_text = state_union.raw("2005-GWBush.txt")
sample_text = state_union.raw("2006-GWBush.txt")

custom_sent_tokenizer = PunktSentenceTokenizer(train_text)



def process_content(tweet):
    tokenized = custom_sent_tokenizer.tokenize(tweet)
    try:
        for i in tokenized:
            words = nltk.word_tokenize(i)
            tagged = nltk.pos_tag(words)
            
            chunkGram = r"""Chunk : {<IN>(<NN>+|<NNP>+|<NNS>+|<NNPS>+)+}"""
            chunkParser = nltk.RegexpParser(chunkGram)
            chunked = chunkParser.parse(tagged)
            location=""
            #chunked.draw()
            for subtree in chunked.subtrees():
                if subtree.label() == 'Chunk':
                    try:
                        for i in range(1,5):
                            location = location + str(subtree[i][0]) + ' '
                    except Exception as e:
                        pass
                    
        return location                     
    except Exception as e:
        print(str(e))
        
loc = process_content()
print(loc)
