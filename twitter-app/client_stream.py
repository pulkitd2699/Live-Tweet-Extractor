from tweepy import API
from tweepy import Cursor
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

import credentials, keywords

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
import json
import string
import pymysql
from sqlalchemy import create_engine

import nltk
from nltk.corpus import state_union
from nltk.tokenize import PunktSentenceTokenizer

train_text = state_union.raw("2005-GWBush.txt")
custom_sent_tokenizer = PunktSentenceTokenizer(train_text)

class TwitterClient():
    def __init__(self, twitter_user=None):
        self.auth = TwitterAuthenticator().authenticate_twitter_app()
        self.twitter_client = API(self.auth, wait_on_rate_limit=True)
        self.twitter_user = twitter_user

    def get_twitter_client_api(self):
        return self.twitter_client

    def get_user_timeline_tweets(self, num_tweets):
        tweets = []
        for tweet in Cursor(self.twitter_client.user_timeline, id=self.twitter_user).items(num_tweets):
            tweets.append(tweet)
        return tweets
    
class TwitterAuthenticator():

    def authenticate_twitter_app(self):
        auth = OAuthHandler(credentials.CONSUMER_KEY, credentials.CONSUMER_SECRET)
        auth.set_access_token(credentials.ACCESS_TOKEN, credentials.ACCESS_TOKEN_SECRET)
        return auth

class TwitterStreamer():
    """
    Class for streaming and processing live tweets
    """
    def __init__(self):
        self.twitter_authenticator = TwitterAuthenticator()

    def stream_tweets(self, fetched_tweets_filename, hash_tag_list):
        #this handles twitter authentication and the connection to the Twitter Streaming API
        listener = TwitterListener(fetched_tweets_filename)
        auth = self.twitter_authenticator.authenticate_twitter_app()
        stream = Stream(auth, listener)

        stream.filter(track = hash_tag_list)
    
class TweetAnalyzer():
    
    def hashtag_info(self, tweet):
        hash1 = re.findall(r"#(\w+)",tweet)
        tag = hash1[0]
        tag = tag.replace("iF", "i F")
        tag = tag.replace("if", "i f")
        tag = tag.replace("nW", "n W")
        tag = tag.replace("nw", "n w")
        tag = tag.replace("lE", "l E")
        tag = tag.replace("le","l e")
        tag = tag.split(' ')
        location = tag[0]
        disaster = tag[1]
        return location,disaster

    def tweet_to_dataframe(self, tweets):
        # df = pd.DataFrame(data=[i for i in range(1,len(tweets)+1)], columns=['Index'])
        df = pd.DataFrame(data=[tweet.created_at for tweet in tweets], columns=['Created_at'])
        # df['Created_at'] = np.array([tweet.created_at for tweet in tweets])
        df['Text'] = np.array([tweet.text for tweet in tweets])
        # print(type(tweets[0].text))
        loc=[]
        dis=[]
        for i in range(len(tweets)):
            l,d = self.hashtag_info(tweets[i].text)
            loc.append(l)
            dis.append(d)
        df['Disaster'] = np.array(dis)
        df['Location'] = np.array(loc)
        df.to_csv(r'table1.txt', sep = ' ', mode='w')
        return df

class TweetInfo():

    def clean_tweet(self, tweet):
        inclean_tweet = re.sub(r"http\S+","",tweet)
        words = inclean_tweet.split()
        words = [word.lower() for word in words]
        table = str.maketrans('','',string.punctuation)
        stripped = [w.translate(table) for w in words]
        new_tweet = ' '.join(stripped)
        return new_tweet
    
    def number_tweet(self, tweet):
        tokenized = custom_sent_tokenizer.tokenize(tweet)
        try:
            for i in tokenized:
                words = nltk.word_tokenize(i)
                tagged = nltk.pos_tag(words)
                
                chunkGram = r"""Chunk: {<CD>+}"""
                chunkParser = nltk.RegexpParser(chunkGram)
                chunked = chunkParser.parse(tagged)
                
                #print(chunked.label())
                for subtree in chunked.subtrees():
                    if subtree.label() == 'Chunk':
                        return subtree[0][0]
                
        except Exception as e:
            print(str(e))
    
    def loc_tweet(self, tweet):
        tokenized = custom_sent_tokenizer.tokenize(tweet)
        try:
            for i in tokenized:
                words = nltk.word_tokenize(i)
                tagged = nltk.pos_tag(words)
                
                chunkGram = r"""Chunk : {<IN>(<NN>+|<NNP>+|<NNS>+|<NNPS>+|<JJ>+)+}"""
                chunkParser = nltk.RegexpParser(chunkGram)
                chunked = chunkParser.parse(tagged)
                # print(chunked)
                location=""
                #chunked.draw()
                for subtree in chunked.subtrees():
                    if subtree.label() == 'Chunk':
                        try:
                            for i in range(1,10):
                                location = location + str(subtree[i][0]) + ' '
                        except Exception as e:
                            pass           
            return location                     
        except Exception as e:
            print(str(e))

    def type_of_person(self, tweet):
        in_need = ["please","stuck","send","require","want","need","urgently"]
        tokenized = tweet.split()
        flag=-1
        output=0
        for i in tokenized:
            for j in in_need:
                if i == j:
                    flag = 1
                    output = 1
                    break
                    
            if flag == 1:
                break

        return output

    def tweet_to_dataframe2(self, tweets):
        location=[]
        contact=[]
        top=[]
        for i in range(len(tweets)):
            tweet = tweets[i]
            cleaned = self.clean_tweet(tweet)
            number = self.number_tweet(cleaned)
            contact.append(number)
            place = self.loc_tweet(cleaned)
            location.append(place)
            type_person = self.type_of_person(cleaned)
            if type_person == 1:
                top.append("in_need")
            elif type_person == 0:
                top.append("can_help")

        # print(contact)
        # print(location)
        # print(top)

        df2 = pd.DataFrame()
        df2["Location"] = np.array(location)
        df2["Contact"] = np.array(contact)
        df2["TOP"] = np.array(top)
        df2.to_csv(r'table2.txt', sep = ' ', mode='w')
        return df2

class SaveDatabase():

    def conn(self):
        host="siheternalvoid.cnqwzfu0zufz.ap-south-1.rds.amazonaws.com"
        port=3306
        dbname="temp"
        user="EternalVoid"
        password="paneerbuttermasala"

        try:
            conn = pymysql.connect(host, user=user, port=port, passwd=password,db=dbname)
            return conn
        except Exception as e:
            print(e)
        
    def df1_to_db(self, df):
        engine = create_engine("mysql+pymysql://{user}:{pw}@siheternalvoid.cnqwzfu0zufz.ap-south-1.rds.amazonaws.com/{db}"
                       .format(user="EternalVoid",
                               pw="paneerbuttermasala",
                               db="temp"))
        df.to_sql('disaster', con=engine,if_exists='append',chunksize=1000)
    
    def df2_to_db(self, df):
        engine = create_engine("mysql+pymysql://{user}:{pw}@siheternalvoid.cnqwzfu0zufz.ap-south-1.rds.amazonaws.com/{db}"
                       .format(user="EternalVoid",
                               pw="paneerbuttermasala",
                               db="temp"))
        df2.to_sql('people', con=engine,if_exists='append',chunksize=1000)

if __name__ == "__main__":
    twitter_client = TwitterClient()
    tweet_analyzer = TweetAnalyzer()
    tweet_info = TweetInfo()
    save_db = SaveDatabase()

    api = twitter_client.get_twitter_client_api()
    tweets = api.user_timeline(screen_name="sihvoid", count = 30)
    # print(dir(tweets[0]))
    df = tweet_analyzer.tweet_to_dataframe(tweets)
    # print(df.head())
    table = df["Text"]
    tweet_list = table.values.tolist()
    df2 = tweet_info.tweet_to_dataframe2(tweet_list)
    # print(df2.head())

    print(save_db.conn())
    save_db.df1_to_db(df)
    save_db.df2_to_db(df2)
