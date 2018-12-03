#! /usr/bin/python

from simpleVirt.simpleVirt import simpleVirt
from remoteApp.remoteApp import remoteApp

from mailMe.mailMe import mailMe
from util.printer import printer
from util.thread import thread
import timeit
import traceback
# Scaling module

EXECUTE_COMMAND_1 = 0
EXECUTE_COMMAND_2 = 1


class scaling:

    def __init__(self, inputParser):
        self.configInfo = inputParser.configInfo
        self.hostsInfo = inputParser.hostsInfo
        self.guestInfo = inputParser.guestInfo
        self.appInfo = inputParser.appInfo
        self.migrationInfo = inputParser.migrationInfo
        self.csvInfo = inputParser.csvInfo
        self.mailMeInfo = inputParser.mailMeInfo
        self.ssh_repeat = int(self.appInfo["ssh_repeat"])

        self.printer = printer(self.configInfo["verbose"])

        self.mail = None
        
        self.machineConfig = inputParser.machineConfig

        if self.configInfo["mailme"]:
            self.mail = mailMe(self.mailMeInfo)

        self.virt = simpleVirt(self.printer, self.hostsInfo, self.guestInfo, self.appInfo)

    def run(self):
        print "run scale"
        exec_num = 1

        if self.configInfo["repeat"]:
            exec_num = int(self.appInfo["repeat_num"])
            
        for i in range(exec_num):
            self.printer.puts("Controle: running test " + str(i + 1))
            
            status = self.__runTestScale()
            if not status:

                if self.mail:
                    self.mail.send_email_warning(
                        subject="Error: " + self.csvInfo["name"], body="Error test " + str(i + 1))

                self.virt.forceDestroyDom()
                
            else:

                if self.mail:
                    self.mail.send_email(
                        subject="Success: " + self.csvInfo["name"])

            self.printer.puts("###########\n\n")

    def __runTestScale(self):
        status = True

        try:
            
            start_time = timeit.default_timer()

            src = self.virt.connect2Host(self.hostsInfo["src"], self.guestInfo["hypervisor"])
            
            dom = self.virt.getDomByName(self.guestInfo["name"],src)
            
            self.virt.config(dom, int(self.machineConfig["vcpu_start"]),int(self.machineConfig["memory_start"]),int(self.machineConfig["max_memory"]))
            
            dom = self.virt.startDom(self.guestInfo["name"], src)
            
            self.virt.wait4Connection(self.ssh_repeat)
            
            setup_time = timeit.default_timer()
            
            app = remoteApp(self.printer, self.appInfo, self.guestInfo,EXECUTE_COMMAND_1)
            app2 = remoteApp(self.printer, self.appInfo, self.guestInfo,EXECUTE_COMMAND_2)
            # start new thread and exec application
            thread1 = self.__execThread(app)
                           
            
            thread1.join()
            first_part_time = timeit.default_timer()
            
            self.virt.scale(dom,  int(self.machineConfig["vcpu_end"]),int(self.machineConfig["memory_end"]))
            
            scale_time = timeit.default_timer()
            
            #thread1 = self.__execThread(app)
            
            thread1.join()
            
            thread1 = self.__execThread(app2)
            
            thread1.join()
            
            second_part_time = timeit.default_timer()
            
            out, err, code, runtime = app.getAppOutput()

            if code == 0:
                self.printer.puts("Application Finished with sucess")
                self.printer.puts("application runtime: " + str(runtime))
                #self.printer.puts(out)
            else:
                 self.printer.puts("Application Finished with error", True)
                 self.printer.puts(err, True)
                 self.printer.puts(out, True)
                 print "Erro code: ", code
                 if self.configInfo["csv"]:
                    with open(self.csvInfo["path"] + self.csvInfo["name"], "a") as csv:
                        csv.write("Next result has errors\n")
                 
             # output csv
            if self.configInfo["csv"]:
                 with open(self.csvInfo["path"] + self.csvInfo["name"], "a") as csv:
                     csv.write(
                         
                         "vcpu"+self.machineConfig["vcpu_start"]+"mem"+self.machineConfig["memory_start"]+" -> "+"vcpu"+self.machineConfig["vcpu_end"]+"mem"+self.machineConfig["memory_end"]
                         
                         
                         +","+str(setup_time - start_time)+ "," + str(first_part_time - setup_time)+ "," + str(scale_time - first_part_time)+ "," + str(second_part_time - scale_time)+ "," + str(second_part_time - start_time) + "\n")

            # finish environment

            self.virt.destroyDom(dom)
            src.close()
            app.closeSSH()
            finish_time = timeit.default_timer()
        except Exception as e:
            self.printer.puts("ERROR: main test error", True)
            status = False
            print e
            traceback.print_exc()
            

        return status

    def __execThread(self, app):
        
        def __manager_app(app):
            app.execApp()

        t1 = thread(__manager_app, app)
        t1.start()

        return t1
