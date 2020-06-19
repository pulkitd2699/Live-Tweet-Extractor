from tweepy import API
from tweepy import Cursor
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

import credentials, keywords

from textblob import TextBlob

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re

# # # Twitter Client # # #
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
    
    def get_friend_list(self, num_friends):
        friend_list = []
        for friend in Cursor(self.twitter_client.friends, id = self.twitter_user).items(num_friends):
            friend_list.append(friend)
        return friend_list

# # # Twitter Authenticator # # #
class TwitterAuthenticator():

    def authenticate_twitter_app(self):
        auth = OAuthHandler(credentials.CONSUMER_KEY, credentials.CONSUMER_SECRET)
        auth.set_access_token(credentials.ACCESS_TOKEN, credentials.ACCESS_TOKEN_SECRET)
        return auth

# # # Twitter Streamer # # #
class TwitterStreamer():
    """
    Class for streaming and processing live tweets
    """
    def __init__(self):
        self.twitter_authenticator = TwitterAuthenticator()

    def stream_tweets(self, fetched_tweets_filename, hash_tag_list):
        #this handles twitter authentication and the connection to the Twitter Streaming API
        listener = TwitterListener(fetched_tweets_filename)
        auth = twitter_authenticator.authenticate_twitter_app()
        stream = Stream(auth, listener)

        stream.filter(track = hash_tag_list)        

# # # Twitter Stream Listener # # #  
class TwitterListener(StreamListener):

    def __init__(self, fetched_tweets_filename):
        self.fetched_tweets_filename = fetched_tweets_filename

    def on_data(self, data):
        try:
            print(data)
            with open(self.fetched_tweets_filename, 'a') as tf:
                tf.write(data)
            return True
        except BaseException as e:
            print("Error on_data %s" % str(e))
        return True

    def on_error(self, status):
        if status == 420:
            #Returning False on_data method in case rate limit occurs
            return False
        print(status)
    
class TweetAnalyzer():
    """
    Functionality for analyzing and categorizing content from tweets 
    """
    def clean_tweet(self, tweet):
        return ' '.join(re.sub(r'(@[A-Za-z0-9]+)|([^0-9A-Za-z])', ' ', tweet).split())

    def analyze_sentiment(self, tweet):
        analysis = TextBlob(self.clean_tweet(tweet))

        if analysis.sentiment.polarity > 0:
            return 1
        elif analysis.sentiment.polarity == 0:
            return 0
        else:
            return -1

    def tweets_to_data_frame(self, tweets):
        df = pd.DataFrame(data=[tweet.text for tweet in tweets], columns=['Tweets'])
        
        df['len'] = np.array([len(tweet.text) for tweet in tweets])
        df['date'] = np.array([tweet.created_at for tweet in tweets])
        df['coordinates'] = np.array([tweet.coordinates for tweet in tweets])
        df['likes'] = np.array([tweet.favorite_count for tweet in tweets])
        df['retweets'] = np.array([tweet.retweet_count for tweet in tweets])
        # df['entities'] = np.array([tweet.entities for tweet in tweets])
        # df['geo'] = np.array([tweet.geo for tweet in tweets])
        # df.to_csv(r'info.txt', header = None, sep = ' ', mode='a')
        return df

if __name__ == "__main__":
    fetched_tweets_filename = "tweets.json"
    hash_tag_list = keywords.key_list

    # twitter_client = TwitterClient('devanshi_g25')
    # print(twitter_client.get_user_timeline_tweets(1))
    # num_friends = 20
    # for i in range(num_friends):
        # print(twitter_client.get_friend_list(num_friends)[i]._json['name'])
    # twitter_streamer = TwitterStreamer()
    # twitter_streamer.stream_tweets(fetched_tweets_filename, hash_tag_list)

    twitter_client = TwitterClient()
    tweet_analyzer = TweetAnalyzer()

    api = twitter_client.get_twitter_client_api()

    tweets = api.user_timeline(screen_name="pycon", count=20)
    print(dir(tweets[0]))   #Things that can be extracted from a tweet

    # df = tweet_analyzer.tweets_to_data_frame(tweets)
    # df['sentiment'] = np.array([tweet_analyzer.analyze_sentiment(tweet) for tweet in tweets])

    # print(df.head())

    #VISUALIZING DATA
    """
    #Info about 10 tweets
    print(df.head(10))

    #Get average len over all tweets
    print(np.mean(df['len']))

    # Get the number of likes for the most liked tweets
    print(np.max(df['likes']))

    # Time Series
    time_likes = pd.Series(data=df['likes'].values, index=df['date'])
    time_likes.plot(figsize=(16,4), color='r', label="likes", legend=True)

    time_retweets = pd.Series(data=df['retweets'].values, index=df['date'])
    time_retweets.plot(figsize=(16,4), color='b', label="retweets", legend=True)

    plt.show()
    """

