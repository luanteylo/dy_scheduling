#! /usr/bin/python

from simpleVirt.simpleVirt import simpleVirt
from simpleVirt.remoteApp import remoteApp

from mailMe.mailMe import mailMe
from util.printer import printer
from util.thread import thread


class scaling:

    def __init__(self, inputParser):
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

        self.virt = simpleVirt(self.printer, self.hostsInfo, self.guestInfo)

    def run(self):

        self.__runTestScale()

    def __runTestScale(self):
        status = True

        try:

            src = self.virt.connect2Host(self.hostsInfo["src"])
            dest = self.virt.connect2Host(self.hostsInfo["dest"])

            dom = self.virt.startDom(self.guestInfo["name"], src)

            # app = RemoteApp(printer, app_info, guest_info)
            # start new thread and exec application
            # thread1 = execThread(app)

            self.virt.scale(dom, 3, 2000)
            # thread1.join()
            # out, err, code, runtime = app.getAppOutput()

            # if code == 0:
            # 	self.printer.puts("Application Finished with sucess")
            #     self.printer.puts("application runtime: " + str(runtime))
            #     # self.printer.puts(out)
            # else:
            #     self.printer.puts("Application Finished with error", True)
            #     self.printer.puts(err, True)
            #     self.printer.puts(out, True)
            #     print "Erro code: ", code
            # # output csv
            # if self.configInfo["csv"]:
            #     with open(self.csvInfo["path"] + self.csvInfo["name"], "a") as csv:
            #         csv.write(str(runtime) + "\n")

            # finish environment

            self.virt.destroyDom(dom)
            src.close()
            dest.close()
            # app.closeSSH()
        except Exception as e:
            self.printer.puts("ERROR: main test error", True)
            status = False
            print e
            

        return status
