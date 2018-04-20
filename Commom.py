#! /usr/bin/python

import ConfigParser

import threading
import sys


if len(sys.argv) <= 1:
    print "Arg error - controler.conf not found"


Config = ConfigParser.ConfigParser()
Config.read(sys.argv[1])


def getSections(section, booltype=False):
    dict1 = {}

    try:
        options = Config.options(section)
    except ConfigParser.NoSectionError:
        print "Exception: Section '%s' Not Found" % section
        exit(1)
    
    for option in options:
        try:
            if not booltype:
                dict1[option] = Config.get(section, option)            
            else:
                dict1[option] = Config.getboolean(section, option)       
        except:
            print "exception on %s!" % option
            dict1[option] = None
    return dict1


class Print_Wrapper:

    def __init__(self, config):
        self.config = config
        self.verbose =  self.config["verbose"]

    def puts(self, content, warning=False):

        if self.verbose or warning:
            print content
 
class FuncThread(threading.Thread):
    def __init__(self, target, *args):
        self._target = target
        self._args = args
        threading.Thread.__init__(self)
 
    def run(self):
        self._target(*self._args)
 
# # Example usage
# def someOtherFunc(data, key):
#     print "someOtherFunc was called : data=%s; key=%s" % (str(data), str(key))
 
# t1 = FuncThread(someOtherFunc, [1,2], 6)
# t1.start()
# t1.join()

