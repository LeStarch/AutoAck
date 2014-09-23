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

class NullPlugin(object):
    '''
    A do-nothing pluign to catalyze the system.
    Boom!  KaBoom!
    '''
    def __init__(self,conn):
        self.conn = conn 
    def run(self,user,message):
        pass
    def list(self):
        pass

class PluginLoader(object):    
    '''
    This class loads and check plugins.
    '''
    def __init__(self, plugs, conn):
        '''
        Initializes the plugins.
        plugins - list of python classes representing plugins
        '''
        self.conn = conn
        self.plugins = []
        plugs.insert(0, "plugins.plugin") #Add in our module (containing the NullPlugin)
        for plug in plugs:
            self.load(plug,conn)
    def load(self,module,conn):
        '''
        Load a plugin's module, and scan for classes implementing 
        a run method accepting 'user' and 'message' arguments. 
        '''
        print "Loading plugins from ",module
        importlib.import_module(module)
        classes = inspect.getmembers(sys.modules[module], inspect.isclass)
        for clazz in classes:
            print "Checking class: ", clazz[0]
            if self.checkPlugin(clazz):
                print "Successfully loaded plugin: ", clazz[0]
                self.plugins.append(clazz[1](conn))
        
    def checkPlugin(self, plugin): 
        '''
        Checks if a class from the "plugin" module is properly duck-typed.
        Properly typed has "run" method with 2 args (and "self" arg) and
        a list method that reports a list of commands.
        @return: True, if valid plugin, False if not
        '''
        for spec in [("run",3),("list",1)]: 
            fun = getattr(plugin[1], spec[0], None)
            if fun is None or len(inspect.getargspec(fun)[0]) != spec[1]:
                print "Class: ", plugin[0], " does not implement ", spec[0], " with ", str(spec[1]), " arguments."
                return False
        return True
    def runAll(self,user,message):
        '''
        Run every plugin.
        user - username of the message reporter
        message - message that was sent
        @return: List of results of all plugins
        '''
        rets = []
        for plugin in self.plugins:
            print "Running: ", plugin
            #Don't perish on malformed plugin
            try:
                rets.append(plugin.run(user, message))
            except Exception as e:
                #Remove failing plugins   
                print "Plugin failing: ", plugin, " Error: ", e
                self.plugins.remove(plugin)
                
                #TODO: Notify cmd line of failure
        return rets
    def listAll(self):
        '''
        Lists all plugins prepending their names.
        '''
        for plugin in self.plugins:
            print "Listing:",plugin
            #Don't perish on malformed plugin
            try:
                rmap = plugin.list()
                if rmap is None:
                    continue
                for name,cmdlist in rmap.iteritems():
                    self.conn.send(name+": [" + ", ".join(cmdlist)+"]")
            except Exception as e:
                #Remove failing plugins   
                print "Plugin failing: ", plugin, " Error: ", e
                self.plugins.remove(plugin)
