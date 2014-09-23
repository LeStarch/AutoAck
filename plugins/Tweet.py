'''
Created on Sep 19, 2014

@author: mstarch

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
'''
Pulled the twitter plugin out into its own module.

Thanks to: Hector?
'''
import ConfigParser
import json
from irc import utilities

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import API


class TweetPlugin:
    ''' Catches the "autotweet" command '''
    def __init__(self):
        ''' Initialize twitter '''
        config = ConfigParser.ConfigParser()
        config.read('.twitter')

        consumer_key = config.get('apikey', 'key')
        consumer_secret = config.get('apikey', 'secret')
        access_token = config.get('token', 'token')
        access_token_secret = config.get('token', 'secret')
        stream_rule = config.get('app', 'rule')
        account_screen_name = config.get('app', 'account_screen_name').lower() 
        self.account_user_id = config.get('app', 'account_user_id')

        self.auth = OAuthHandler(consumer_key, consumer_secret)
        self.auth.set_access_token(access_token, access_token_secret)
        self.twitterApi = API(self.auth)
    def list(self):
        pass
    def run(self,user,message):
        if utilities.getCommand() == "autotweet":
            streamListener = ReplyToTweet()
            streamListener.setAPI(self.twitterApi)
            streamListener.setUser(self.account_user_id)
            twitterStream = Stream(self.auth, streamListener)
            twitterStream.userstream(_with='user')


class ReplyToTweet(StreamListener):
    '''
    # Monitor the user account for the given twitter account.
    # Auto-reply Ack to any tweet to that user stream
    # https://dev.twitter.com/docs/streaming-apis/streams/user
    '''
    def setAPI(self,api):
        ''' Set the API '''
        self.twitterApi = api
    def setUser(self,user):
        ''' Set twitter id '''
        self.account_user_id = user
    def on_data(self, data):
        print data
        tweet = json.loads(data.strip())
        
        retweeted = tweet.get('retweeted')
        from_self = tweet.get('user',{}).get('id_str','') == self.account_user_id

        if retweeted is not None and not retweeted and not from_self:

            tweetId = tweet.get('id_str')
            screenName = tweet.get('user',{}).get('screen_name')
            tweetText = tweet.get('text')

            replyText = '@' + screenName + ' ' + 'ACK ' + tweetText #This could be chatResponse but for now is just ACK

            #check if repsonse is over 140 char
            if len(replyText) > 140:
                replyText = replyText[0:137] + '...'

            print('Tweet ID: ' + tweetId)
            print('From: ' + screenName)
            print('Tweet Text: ' + tweetText)
            print('Reply Text: ' + replyText)

            # If rate limited, the status posts should be queued up and sent on an interval
            self.twitterApi.update_status(replyText, tweetId)

    def on_error(self, status):
        print status