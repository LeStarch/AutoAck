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
#Import lib used to load modules by name, and find modules
import importlib
import inspect
import sys
import irc.utilities

class NullPlugin:
    '''
    A do-nothing pluign to catalyze the system.
    Boom!  KaBoom!
    '''
    def __init__(self):
        pass 
    def run(self,user,message):
        pass

class PluginLoader(object):    
    '''
    This class loads and check plugins.
    '''
    def __init__(self, plugs):
        '''
        Initializes the plugins.
        plugins - list of python classes representing plugins
        '''
        self.plugins = []
        plugs.insert(0, "plugins.plugin") #Add in our module (containing the NullPlugin)
        for plug in plugs:
            self.load(plug)
    def load(self,module):
        '''
        Load a plugin's module, and scan for classes implementing 
        a run method accepting 'user' and 'message' arguments. 
        '''
        importlib.import_module(module)
        classes = inspect.getmembers(sys.modules[module], inspect.isclass)
        for clazz in classes:
            if self.checkPlugin(clazz):
                self.plugins.append(clazz())
        
    def checkPlugin(self, plugin): 
        '''
        Checks if a class from the "plugin" module is properly duck-typed.
        Properly typed has "run" method with 2 args (and "self" arg) and
        a list method that reports a list of commands.
        @return: True, if valid plugin, False if not
        '''
        fun = getattr(plugin, "run", None)
        if fun is None and len(inspect.getargspec(fun)[0]) == 3:
            return False
    
    def run(self,user,message):
        '''
        Run every plugin.
        user - username of the message reporter
        message - message that was sent
        @return: List of results of all plugins
        '''
        rets = []
        for plugin in self.plugins:
            #Don't perish on malformed plugin
            try:
                rets.append(plugin.run(user, message))
            except:
                #Remove failing plugins
                self.plugins.remove(plugin)
                #TODO: Notify cmd line of failure
        return rets
    def list(self):
        '''
        Lists all plugins prepending their names.
        '''
        for plugin in self.plugins:
            #Don't perish on malformed plugin
            try:
                rmap = plugin.list()
                for name,cmdlist in rmap.iteritems():
                    irc.utilities.send(name+": [" + ", ".join(cmdlist))
            except:
                #Remove failing plugins
                self.plugins.remove(plugin)
                #TODO: Notify cmd line of failure