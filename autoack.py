'''
Copyright 2014 Tyler Palsulich

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Refactored by: starchmd

'''

# This bot is a result of a tutoral covered on http://shellium.org/wiki.
import sys
import argparse
import irc.irc
from datetime import datetime
from datetime import timedelta

from plugins.plugin import PluginLoader

class Mute():
    ''' A timing mute for the AutoAck system '''
    def __init__(self):
        ''' CTor '''
        self.time = datetime.now()
    def silenceFor(self,seconds):
        ''' Silence for "seconds" seconds. '''
        if seconds > 0:
            self.time = datetime.now() + timedelta(seconds=seconds)
        else:
            self.time = datetime.now()
    def canSend(self):
        ''' Check if we can send '''
        return datetime.now() > self.time

def main_loop(conn):
    '''
    Loop forever processing messages as they come. 
    conn - connection to irc (see irc.irc.IRC)
    '''
    mute = Mute()
    plugsys = PluginLoader()
    while True:
        message = conn.recv()
        print message
    
        # Only respond to chat from the current chatroom (not private or administrative log in messages).
        if conn.getSplitter() not in message:
            continue
    
        # Get the content of the message.
        user = message.split("!")[0][1:]
        message = message.split(conn.getSplitter())[1]
    
        # Convert to lowercase and split the message based on whitespace.
        split = message.lower().split()
        if split[0] == args.nick.lower() + ":":   # Command addressed to the bot (e.g. learn or forget).
            if split[1] == "quiet" and len(split) <= 3:
                mute.silenceFor(args.seconds if len(split) ==2 else int(split[2]) )
                conn.send("Whatever you say.", user, True)
            elif split[1] == "speak" and len(split) == 2:
                mute.silenceFor(0)
            elif split[1] == "list" and len(split) == 2:
                plugsys.list()
        elif mute.canSend():
            plugsys.run(user,message)

if __name__ == '__main__':
    ''' Main method'''
    try:
        parser = argparse.ArgumentParser(description='An IRC bot used to respond to keywords automatically.')
        parser.add_argument('-n', '--nick',    default='AutoAck',           help='Username of the bot')
        parser.add_argument('-s', '--server',  default='chat.freenode.net', help='Server to connect to')
        parser.add_argument('-q', '--quiet',   default=30,   type=int,      help='Default number of seconds to stay quiet when told')
        parser.add_argument('-p', '--port',    default=6667, type=int,      help='Port to use when connecting to the server.')
        parser.add_argument('channel',                                      help='Channel to connect to.')  
        args = parser.parse_args()
        #Force channel to start with #
        if args.channel[0] != "#":
            args.channel = "#" + args.channel
        conn = irc.irc.IRC(args.nick,args.channel,args.server,args.port)
        main_loop(conn)
    except KeyboardInterrupt:
        print >> sys.stderr, '\nExiting by user request.\nAufwiedersehen mien Freund.\n再見，我的朋友.\n'
        sys.exit(0)
