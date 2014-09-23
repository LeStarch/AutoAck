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
'''
Contains the standard plugins created by Tyler et. al.
    Parrot  - Standard responses to standard command.
    Padiwan - Allows learning of new parrot commands.
    Help    - Sends the help.
'''
class ParrotPlugin(object):
    '''
    Repeats specific responses for specific inputs.
    '''
    def __init__(self, conn):
        # Map from keywords to how the bot will respond in chat.
        self.conn = conn
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
        #Don't spam on commands
        if self.conn.isPersonal(message):
            return
        for key in self.responces:
            if key in message:
                self.conn.send((self.responces[key] + " ") * message.count(key, 0))
    def list(self):
        '''Reports default commands.'''
        return {"Default Commands: ":self.responces.keys()}
    
class Padiwan(ParrotPlugin):
    def __init__(self,conn):
        ''' Init '''
        super(Padiwan,self).__init__(conn)
        self.defaults = self.responces
        self.authors = {}
        self.responces = shelve.open("autoack.shelf")
        atexit.register(self.responces.close)
    def learn(self,cmd,response, user):
        ''' Learn a command '''
        if cmd not in self.defaults:
            self.conn.send(("Relearned" if cmd in self.responces else "Learned")+ " "+cmd)
            self.responces[cmd] = " ".join(response)
            self.authors[cmd] = user
        else:
            self.conn.send("Go away, " + user + "!")
    def forget(self,cmd):
        ''' Forget a command '''
        if cmd in self.defaults:
            self.conn.send("No.")
        elif cmd in self.responces:
            self.responces.pop(cmd) 
            self.conn.send("Dropped like a bad habit.")
        else:
            self.conn.send("Maybe you're the one forgetting...")
    
    def run(self,user,message):
        '''Runs a command'''
        cmd = self.conn.getCommand(message)
        args = self.conn.getArgs(message)
        if cmd == "learn" and len(args) >= 2:
            self.learn(args[0],args[1:],user)
        elif cmd == "forget" and len(args) == 1:
            self.forget(args[0])
        elif cmd == "blame" and len(args) == 1:
            self.conn.send(args[0] + " was created by " + self.authors[args[0]], user)
        elif cmd == "learn" or cmd == "forget" or cmd == "blame":
            self.conn.send("Incomplete command.",user)
        else:
            super(Padiwan,self).run(user,message)
    def list(self):
        '''Reports learned commands.'''
        return {"Learned Commands: ":self.responces.keys()}  

class Help(object):
    def __init__(self,conn):
        '''Initialize yo'''
        self.conn = conn
    def list(self):
        ''' Do nothing '''
        pass
    def run(self,user,message):
        ''' Check for help, and print help. '''
        cmd = self.conn.getCommand(message)
        if cmd == "help":
            nick = self.conn.getNick()
            self.conn.send("Available commands:")
            self.conn.send("   " + nick + ": autotweet (monitor the defined twitter account and AutoAck Tweets)")
            self.conn.send("   " + nick + ": blame [key] (show user who created [key])")
            self.conn.send("   " + nick + ": forget [key] (forget user learned keyword [key])")
            self.conn.send("   " + nick + ": help (print this help message)")  
            self.conn.send("   " + nick + ": learn [key] [value] (learn to say [value] after [key])")
            self.conn.send("   " + nick + ": list (print list of available keywords)")
            self.conn.send("   " + nick + ": quiet [seconds] (don't talk for optional number of [seconds])")
            self.conn.send("   " + nick + ": speak (override a previous quiet command)")
            self.conn.send("   " + nick + ": tweet (send a tweet to the defined twitter account)")  
    