'''
Copyright 2014 starchmd

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
stdout=True

def getNick():
    ''' Get the Nick of this AutoAck '''
    return "dumby-nick"

def send(message):
    ''' A command that handles sending data to IRC '''
    if stdout:
        print(message)
    else:
        irc.send(message)
    


def isPrivate(message):
    ''' Checks to see if the message is private '''
    split = message.lower().split()
    return split[0] == getNick().lower() + ":"

def getCommand(message):
    ''' Returns the command '''
    if isPrivate(message):
        return message.lower().split()[1]
    return None

