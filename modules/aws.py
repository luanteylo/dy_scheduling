#! /usr/bin/python

#from simpleVirt.simpleVirt import simpleVirt


from simpleBoto.simpleBoto import  simpleBoto


from remoteApp.remoteAppAws import remoteAppAws

from mailMe.mailMe import mailMe
from util.printer import printer
from util.thread import thread

import traceback
import timeit
import sqlite3
import os


# test

class aws:

    # get the input parameters
    def __init__(self, inputParser):
        '''
        inputParser : util.inputParser
        '''

        self.configInfo = inputParser.configInfo
        self.ec2Info = inputParser.ec2Info
        self.appInfo = inputParser.appInfo
        self.csvInfo = inputParser.csvInfo
        self.mailMeInfo = inputParser.mailMeInfo
        self.ssh_repeat = int(self.appInfo["ssh_repeat"])
        self.dbInfo = inputParser.dbConfig

        self.printer = printer(self.configInfo["verbose"])

        self.mail = None
        if self.configInfo["mailme"]:
            self.mail = mailMe(self.mailMeInfo)

        self.boto = simpleBoto(self.printer, self.ec2Info,  self.appInfo)



    def __openDB(self):
        pass


    def run(self):
        
        exec_num = 1
        if self.configInfo["repeat"]:
           exec_num = int(self.appInfo["repeat_num"])
            
        for i in range(exec_num):
           status = self.__runTest()
                
                

    def __runTest(self):
        status = True
        
        start_time = timeit.default_timer()

            #src = self.virt.connect2Host(self.hostsInfo["src"])
            

        instances = self.boto.create_instances(self.ec2Info["start_type"])

        

        #dest = self.virt.connect2Host(self.hostsInfo["dest"])
        for instance in instances:
            #START TEST
            start_time = timeit.default_timer()
            
            
            
            
            self.boto.wait4Connection(self.ssh_repeat, instance)
            app = remoteAppAws(self.printer, self.appInfo, self.ec2Info, instance.public_dns_name,0)
            
            # STOP SETUP
            setup_time = timeit.default_timer()
            
            
            
            # start new thread and exec application
            thread1 = self.__execThread(app)
            
            thread1.join()
            
            #END FIRST PART
            first_part_time = timeit.default_timer()
            
            self.boto.make_vertical_migration(instance, self.ec2Info["end_type"])
            
            
            self.boto.wait4Connection(self.ssh_repeat, instance)
            
            #END SCALE
            scale_time = timeit.default_timer()
            
            app2 = remoteAppAws(self.printer, self.appInfo, self.ec2Info, instance.public_dns_name,1)
            thread2 = self.__execThread(app2)
            thread2.join()
            
            #END SECOND PART
            second_part_time = timeit.default_timer()
            
            
            self.boto.terminate_instance(instance.id)
            
            
            
            #src.close()
            #dest.close()
            app.closeSSH()
            end_time = timeit.default_timer()
            # output csv
            if self.configInfo["csv"]:
                with open(self.csvInfo["path"] + self.csvInfo["name"], "a") as csv:
                    csv.write("vcpu"+self.ec2Info["start_type"]+" -> "+"vcpu"+self.ec2Info["end_type"]
                         
                         
                         +","+str(setup_time - start_time)+ "," + str(first_part_time - setup_time)+ "," + str(scale_time - first_part_time)+ "," + str(second_part_time - scale_time)+ "," + str(end_time - start_time) + "\n")

            
            
            
            
            
           

        #except Exception as e:

        #    self.printer.puts("ERROR: error during the test execution", True)
        #    status = False
        #    print e
        #    traceback.print_exc()

        return status

    def __execThread(self, app):
        def __manager_app(app):
            app.execApp()

        t1 = thread(__manager_app, app)
        t1.start()

        return t1
