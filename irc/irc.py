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

Pulled out Tyler's IRC communications into its own class.
'''
import socket
import re
class IRC():
    '''
    Handles IRC setup, destruction, and communication
    '''

    def __init__(self, nick, channel, server, port):
        '''
        Initialize the IRC.
        nick - Nickname for the auto-ack bot.
        channel - Join this specific channel.
        '''
        self.nick = nick
        self.channel = channel
        self.splitter = "PRIVMSG " + self.channel + " :"
        self.ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("[INFO] Attempting to connect to " + server + ":" + self.channel + " on port " + str(port) + " with username " + self.nick)
        self.ircsock.connect((server, port)) # Connect to the server.
        self.ircsock.send("USER " + self.nick + " " + self.nick + " " + self.nick + " :.\n") # Authenticate the bot.
        self.ircsock.send("NICK " + self.nick + "\n") # Assign the nickname to the bot.
        self.rex = re.compile(self.nick+":\s*(\w+)?",re.IGNORECASE)
        self.join(self.channel)

    def getSplitter(self):
        ''' Returns the splitter '''
        return self.splitter

    def send(self, message, user = None):
        ''' Sends a message '''
        if user is None:
            self.ircsock.send("PRIVMSG " + self.channel + " :" + message + "\n")
        else:
            self.ircsock.send("PRIVMSG " + self.channel + " :" + user + ": " + message + "\n")

    def join(self,channel):
        ''' Joins a channel '''
        self.ircsock.send("JOIN " + channel + "\n")
        
    def recv(self):
        ''' Receives a message '''
        message = self.ircsock.recv(2048) # Receive data from the server.
        message = message.strip('\n\r') # Remove any unnecessary linebreaks.
        print(message)
        if "PING :" in message:
            print "-pong-"
            self.pong(message)
        return message

    def pong(self,data):
        '''Pong'''
        self.ircsock.send("PONG " + data.split()[1] + "\n")
    
    def getNick(self):
        '''Return nickname'''
        return self.nick
    
    def isPersonal(self,message):
        ''' Checks to see if the message is private '''
        return not self.rex.search(message) is None
    def getCommand(self,message):
        ''' Returns the command '''
        if self.isPersonal(message):
            mat = self.rex.search(message)
            return mat.group(1)
        return None
    def getArgs(self,message):
        '''Gets the arguments assuming a command.'''
        if self.isPersonal(message):
            tmp = self.rex.sub("",message)
            return tmp.split()
        return []