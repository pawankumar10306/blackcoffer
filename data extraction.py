# Importing nessesary module
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from nltk.tokenize import word_tokenize
from nltk.tokenize import sent_tokenize
import nltk
import os
nltk.download('punkt')
nltk.download("stopwords")

stop_word=[]
for file in os.listdir('StopWords'):
    f=open('stopWords/'+file,'r')
    f=re.sub('[^a-z\s]','',f.read().lower())
    stop_word+=nltk.word_tokenize(f)
# print(stop_word)

positive_word=open('MasterDictionary/positive-words.txt')
positive_word=nltk.word_tokenize(re.sub('[^a-z\s]','',positive_word.read().lower()))
positive_word = list(filter(lambda word: word not in stop_word, positive_word))
# print(positive_word)

negative_word=open('MasterDictionary/negative-words.txt')
negative_word=nltk.word_tokenize(re.sub('[^a-z\s]','',negative_word.read().lower()))
negative_word = list(filter(lambda word: word not in stop_word, negative_word))
# print(negative_word)

input=pd.read_excel('input.xlsx')
output=pd.DataFrame()
url=input.URL
url_id=37
for link in url:
    text=''
    r=requests.get(link)
    soup = BeautifulSoup(r.content, 'html.parser')
      
    try:
        article_title = soup.title.string.split('|')[0].strip()
    except:
        print('Title not found')
    
    try:
        article_text = soup.find_all('div', class_='tdb-block-inner td-fix-index')[14]
    except:
        try:
            article_text = soup.find('div', class_="td-post-content tagdiv-type")
        except:
            print('Page not found')
        
    # print(type(article_title))
    # print(type(article_text))
    text+=article_title
    try:
        text+=article_text.text
    except:
        print('text cannot be written')
    # print(text)
    
    text_word=re.sub('[^a-z\s]','',text.lower())
    text_word=nltk.word_tokenize(text)
    
    text_word = list(filter(lambda word: word not in stop_word, text_word))
    
    word_count=len(text_word)
    
    positive_score=0
    for word in text_word:
        if word in positive_word:
            positive_score+=1
            
    negative_score=0
    for word in text_word:
        if word in negative_word:
            negative_score+=1
    
    polarity_score=(positive_score - negative_score) / ((positive_score + negative_score) + 0.000001)
    
    subjectivity_score = (positive_score + negative_score)/ (word_count + 0.000001)
    
    sentence_count=len(sent_tokenize(text))
    avg_sentence_length=word_count/sentence_count
    
    complex_word_count = 0
    totalvowels=0
    for word in text_word:
        vowels = 0
        if word.endswith(('es', 'ed')):
            pass
        else:
            for w in word:
                if (w == 'a' or w == 'e' or w == 'i' or w == 'o' or w == 'u'):
                    vowels += 1
                    totalvowels+=1
            if (vowels > 2):
                complex_word_count += 1

    percentage_of_complex_word=complex_word_count/word_count
    
    fog_index=0.4*(percentage_of_complex_word+avg_sentence_length)
    
    syllable_per_word=totalvowels/word_count
    
    personal_pronoun=0
    totalchar=0
    for word in text_word:
        totalchar+=len(word)
        if word in ['i', 'we', 'my','ours','us']:
            personal_pronoun+=1
    
    avg_word_length=totalchar/word_count
    
    data=[{'URL_ID':url_id, 'URL':link, 
                    'POSITIVE SCORE':positive_score, 'NEGATIVE SCORE':negative_score, 'POLARITY SCORE':polarity_score,
                    'SUBJECTIVITY SCORE':subjectivity_score, 'AVG SENTENCE LENGTH':avg_sentence_length,
                    'PERCENTAGE OF COMPLEX WORDS':percentage_of_complex_word, 'FOG INDEX':fog_index,
                    'AVG NUMBER OF WORDS PER SENTENCE':avg_sentence_length, 'COMPLEX WORD COUNT':complex_word_count, 
                    'WORD COUNT':word_count,'SYLLABLE PER WORD':syllable_per_word,
                    'PERSONAL PRONOUNS':personal_pronoun, 'AVG WORD LENGTH':avg_word_length}]
    
    output=output._append(data,ignore_index=True)
    url_id+=1
    print(output)
    
output.to_excel('Output Data Structure.xlsx')
            
    