'''
Created on Sep 19, 2014

@author: starchmd

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
import shelve
import atexit
from irc import utilities 
'''
Contains the standard plugins created by Tyler et. al.
    Parrot  - Standard responses to standard command.
    Padiwan - Allows learning of new parrot commands.
    Help    - Sends the help.
'''


class ParrotPlugin:
    '''
    Repeats specific responses for specific inputs.
    '''
    def __init__(self):
        # Map from keywords to how the bot will respond in chat.
        self.responces = {
            "ack":  "ack",
            "git":  "#gitpush",
            "aye":  "aye, mate!",
            "+1":   "+1",
            "boom": "kaboom!!!",
            "beum": "kabeum!!!",
            "bewm": "ba-bewm!!!",
            "seen": "seen like an eaten jelly bean"}
    
    def run(self,user,message):
        ''' Responds to input '''
        for key in self.responces:
            if key in message:
                utilities.send((self.responces[key] + " ") * message.count(key, 0))
    def list(self):
        '''Reports default commands.'''
        return {"Default Commands: ",self.responces.keys()}
    
class Padiwan(ParrotPlugin):
    def __init__(self):
        ''' Init '''
        #Clear defaults
        self.defaults = {}
        self.responces = shelve.open("autoack.shelf")
        atexit.register(user_commands.close)
    def learn(self,cmd,response, user):
        ''' Learn a command '''
        if cmd not in self.defaults:
            utilities.send(("Relearned" if cmd in self.responces else "Learned")+ " "+cmd)
            self.responces[cmd] = " ".join(response)
        else:
            utilities.send("Go away, " + user + "!")
    def forget(self,cmd):
        ''' Forget a command '''
        if cmd in self.defaults:
            utilities.send("No.")
        elif cmd in self.responces:
            self.responces.pop(cmd) 
            utilities.send("Dropped like a bad habit.")
        else:
            utilities.send("Maybe you're the one forgetting...")
    
    def run(self,user,message):
        '''Runs a command'''
        parts = message.split()
        if parts[0] == "learn":
            self.learn(parts[1],parts[2:],user)
        elif parts[0] == "forget":
            self.forget(parts[1])
        else:
            super.run(user,message)
    def list(self):
        '''Reports learned commands.'''
        return {"Learned Commands: ",self.responces.keys()}  

class Help:
    def list(self):
        ''' Do nothing '''
        pass
    def run(self,user,message):
        ''' Check for help, and print help. '''
        cmd = utilities.getCommand()
        if cmd == "help":
            nick = utilities.getNick()
            utilities.send("Available commands:")
            utilities.send("   " + nick + ": autotweet (monitor the defined twitter account and AutoAck Tweets)")
            utilities.send("   " + nick + ": blame [key] (show user who created [key])")
            utilities.send("   " + nick + ": forget [key] (forget user learned keyword [key])")
            utilities.send("   " + nick + ": help (print this help message)")  
            utilities.send("   " + nick + ": learn [key] [value] (learn to say [value] after [key])")
            utilities.send("   " + nick + ": list (print list of available keywords)")
            utilities.send("   " + nick + ": quiet [seconds] (don't talk for optional number of [seconds])")
            utilities.send("   " + nick + ": speak (override a previous quiet command)")
            utilities.send("   " + nick + ": tweet (send a tweet to the defined twitter account)")  
    