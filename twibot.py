#!/usr/bin/python3
from tweepy import StreamListener, Stream
import tweepy
import json
import requests
from dotenv import load_dotenv
import os

class TwitterBot(StreamListener):
    def __init__(self, keywords=[]):
        load_dotenv()
        # Auth env config
        consumer_key = os.getenv("CONSUMER_KEY")
        consumer_secret = os.getenv("CONSUMER_SECRET")
        access_token = os.getenv("ACCESS_TOKEN")
        access_secret = os.getenv("ACCESS_SECRET")
        # Auth handler
        self.auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        self.auth.set_access_token(access_token, access_secret)
        # Telegram config
        self.telegram_token = os.getenv("TELEGRAM_TOKEN")
        self.telgram_room = os.getenv("TELEGRAM_ROOM")
        # Twitter targets to scrape
        self.targets = os.getenv("TARGETS")
        self.keywords = keywords
        #Lo necesito para el fetch del user id
        self.api = tweepy.API(self.auth)

    def telegram_bot_sendtext(self, bot_token, bot_chatID, bot_message):
        send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&text=' + bot_message
        response = requests.get(send_text)

    def on_data(self, data):
        try:
            # process stream data here
            tweet = json.loads(data)
            screen_name = tweet['user']['screen_name']
            user = self.api.get_user(screen_name)

            try:
               text = tweet['extended_tweet']['full_text']
               url = tweet['entities']['urls'][0]['url']
            except:
               text = tweet['text'].lower()
               url = "https://twitter.com/" + screen_name + "/status/" + tweet['id_str']

            enviar = False

            if user.id_str in self.targets:
                if "media" in tweet['entities']:
                    enviar = True
                else:
                    for i in self.keywords:
                        if i.lower() in text:
                           enviar = True
            if enviar:
               self.telegram_bot_sendtext(self.telegram_token, self.telgram_room, url)
        except KeyError:
               print("Tweet deleted or API attribute not found.")

    def on_error(self, status):
         print(status)

if __name__ == "__main__":
    keywords = ["doge", "xrp"]
    bot = TwitterBot(keywords)
    twitterStream = Stream(bot.auth, bot, tweet_mode= 'extended')
    twitterStream.filter(follow=bot.targets.split(";"))
