#! /usr/bin/python

import ConfigParser

class inputParser:

    def __init__(self, file):
        self.config = ConfigParser.ConfigParser()
        if not self.config.read(file):
            raise ValueError, "Failed to open/find config file"

        self.__readValues()
                    


    def __getSections(self, section, booltype=False):
        dict1 = {}

        try:
            options = self.config.options(section)

        except ConfigParser.NoSectionError:
            
            print "Exception: Section '%s' Not Found" % section
            exit(1)
        
        for option in options:
            
            try:
                if not booltype:
                    dict1[option] = self.config.get(section, option)            
                else:
                    dict1[option] = self.config.getboolean(section, option)       

            except:
                
                print "exception on %s!" % option
                dict1[option] = None

        return dict1

    def __readValues(self):
        
        self.hostsInfo = self.__getSections("Hosts")
        self.guestInfo = self.__getSections("Guest")
        self.appInfo = self.__getSections("Application")
        self.configInfo = self.__getSections("Config", True)
        self.mailMeInfo = self.__getSections("mailMe")
        self.csvInfo = self.__getSections("csv")
        self.migrationInfo = self.__getSections("Migration")

        print ""
