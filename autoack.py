# -*- coding: utf-8 -*-
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

def main_loop(conn,plugins,seconds):
    '''
    Loop forever processing messages as they come. 
    conn - connection to irc (see irc.irc.IRC)
    '''
    mute = Mute()
    plugsys = PluginLoader(plugins,conn)
    while True:
        message = conn.recv()
        print 'Message received: "',message,'"'    
        # Only respond to chat from the current chatroom (not private or administrative log in messages).
        if not conn.getSplitter() in message:
            continue
    
        # Get the content of the message.
        user = message.split("!")[0][1:]
        message = message.split(conn.getSplitter())[1]
        
        if conn.isPersonal(message):   # Command addressed to the bot (e.g. learn or forget).
            cmd = conn.getCommand(message)
            args = conn.getArgs(message)
            if cmd == "quiet" and len(args) <= 1:
                secs = seconds if len(args) == 0 else int(args[0])
                mute.silenceFor(secs)
                conn.send("Silence for "+str(secs)+" seconds.", user)
                continue
            elif cmd == "speak":
                mute.silenceFor(0)
                continue
            elif cmd == "list":
                plugsys.listAll()
                continue
        #Plugins may implement bot commands
        if mute.canSend():
            plugsys.runAll(user,message)
        else:
            print "Shhhhhhh...I have to be quiet."

if __name__ == '__main__':
    ''' Main method'''
    try:
        parser = argparse.ArgumentParser(description='An IRC bot used to respond to keywords automatically.')
        parser.add_argument('-n', '--nick',    default='AutoAck',           help='Username of the bot')
        parser.add_argument('-s', '--server',  default='chat.freenode.net', help='Server to connect to')
        parser.add_argument('-q', '--quiet',   default=30,   type=int,      help='Default number of seconds to stay quiet when told')
        parser.add_argument('-p', '--port',    default=6667, type=int,      help='Port to use when connecting to the server.')
        parser.add_argument('-l', '--plugins', default='plugins.standard',  help='Comma separated list of plugins to use')
        parser.add_argument('channel',                                      help='Channel to connect to.')
        
        args = parser.parse_args()
        #Force channel to start with #
        if args.channel[0] != "#":
            args.channel = "#" + args.channel
        try:
            conn = irc.irc.IRC(args.nick,args.channel,args.server,args.port)
        except Exception as e:
            print >> sys.stderr, "\nFailed to connect to channel: ",args.channel," on server: ", args.server, "/",args.port, " as ",args.nick, e
        try:
            plugins = args.plugins.split(",")
        except Exception as e:
            print >> sys.stderr, "\nFailed to parse plugin list: ",args.plugins
        main_loop(conn,plugins,args.quiet)
    except KeyboardInterrupt:
        print >> sys.stderr, '\nExiting by user request.\nAufwiedersehen mien Freund.\n再見，我的朋友.\n'
        sys.exit(0)
