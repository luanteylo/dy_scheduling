#! /usr/bin/python

from simpleVirt.simpleVirt import simpleVirt
from simpleVirt.remoteApp import remoteApp

from mailMe.mailMe import mailMe
from util.printer import printer
from util.thread import thread

import traceback

# test

class aws:

    # get the input parameters
    def __init__(self, inputParser):
        '''
        inputParser : util.inputParser
        '''
        self.configInfo = inputParser.configInfo
        self.hostsInfo = inputParser.hostsInfo
        self.guestInfo = inputParser.guestInfo
        self.appInfo = inputParser.appInfo
        self.migrationInfo = inputParser.migrationInfo
        self.csvInfo = inputParser.csvInfo
        self.mailMeInfo = inputParser.mailMeInfo

        self.printer = printer(self.configInfo["verbose"])

        self.mail = None
        if self.configInfo["mailme"]:
            self.mail = mailMe(self.mailMeInfo)

        self.virt = simpleVirt(self.printer, self.hostsInfo, self.guestInfo, self.appInfo)

    def run(self):

        exec_num = 1

        if self.configInfo["repeat"]:
            exec_num = int(self.appInfo["repeat_num"])

        for i in range(exec_num):
            self.printer.puts("Controle: running test " + str(i + 1))

            status = self.__runTest()

            # test finished without success
            if not status:

                if self.mail:
                    self.mail.send_email_warning(
                        subject="Error: " + self.csvInfo["name"], body="Error test " + str(i + 1))

                self.virt.forceDestroyDom()

            # test finished with success
            else:

                if self.mail:
                    self.mail.send_email(
                        subject="Success: " + self.csvInfo["name"])

            self.printer.puts("###########\n\n")

    def __runTest(self):

        status = True

        try:

            #src = self.virt.connect2Host(self.hostsInfo["src"])
            #dest = self.virt.connect2Host(self.hostsInfo["dest"])


            #dom = self.virt.startDom(self.guestInfo["name"], src)


	    client = self.virt.get_ec2()

	    instances, time = self.virt.create_vms(ec2_client, "ami-5650702d", 1, "t2.micro")

            app = remoteApp(self.printer, self.appInfo, self.guestInfo)

            # start new thread and exec application
            thread1 = self.__execThread(app)

            

            out, err, code, runtime = app.getAppOutput()

            if code == 0:
                self.printer.puts("Application Finished with sucess")
                self.printer.puts("application runtime: " + str(runtime))
                # self.printer.puts(out)

            else:
                self.printer.puts("Application Finished with error", True)
                self.printer.puts(err, True)
                self.printer.puts(out, True)
                print "Erro code: ", code

            # output csv
            if self.configInfo["csv"]:
                with open(self.csvInfo["path"] + self.csvInfo["name"], "a") as csv:
                    csv.write(str(runtime) + "\n")

            # finish environment
            self.virt.destroyDom(dom)

            src.close()
            dest.close()
            app.closeSSH()

        except Exception as e:

            self.printer.puts("ERROR: error during the test execution", True)
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
