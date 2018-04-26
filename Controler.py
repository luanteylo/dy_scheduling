#! /usr/bin/python
import traceback


import libvirt

from mailMe.mailMe import mailMe

import Commom
from  Commom import Print_Wrapper
from RemoteApp import RemoteApp

import time
import sys
import traceback

# Global Setup Vars
hosts_info = Commom.getSections("Hosts")
guest_info = Commom.getSections("Guest")
app_info = Commom.getSections("Application")
migration_info = Commom.getSections("Migration")
mailMe_info = Commom.getSections("mailMe")
config = Commom.getSections("Config", True)
csv_info = Commom.getSections("csv")

action = Commom.getSections("type")

if config["mailme"]:
    mail = mailMe(mailMe_info)
else:
    mail = None

printer = Print_Wrapper(config)



def print_testInfo():
    print "\n\n", 30*"*"
    print "Hosts: " + hosts_info["src"] + " " + hosts_info["dest"]
    print "Guest: " + guest_info["name"]
    print "Application:", "path: ", app_info["path"], "command:", app_info["command"]
    print "Settings: ", "migrate:", config["migrate"], "csv: ", config["csv"],
    print "CSV: ", "path:", csv_info["path"], "name:", csv_info["name"]
    print 30*"*", "\n\n"

## Virsh Wrapper Functions  ##

def connect2Host(host):
    conn = libvirt.open('qemu+ssh://'+host+'/system')
    if conn == None:
        printer.puts('Failed to connect to the hypervizor', True)
    else:
        printer.puts('Qemu Connected to ' + host)

    return conn

def getDomByName(name, conn):
    try:
        dom = conn.lookupByName(name)
    except libvirt.libvirtError:
        printer.puts('Dominio ' + name + ' was not defined.')
        return None

    return dom

def startDom(name, conn):
    try:
        dom = getDomByName(name, conn)
        dom.create()
    except libvirt.libvirtError as e:
        printer.puts("Controler - startDom: libvirtError", True)
        raise

    printer.puts('Dominio ' + name + ' was started.')
    return dom

def destroyDom(dom):
    try:
        dom.destroy()
    except libvirt.libvirtError as e:
        printer.puts("Controler - destroyDom: libvirtError", True)
        return None                

    printer.puts('Dominio  was destroyed.')
    return dom

def migrate(src, dest, dom):
    try:
        new_dom = dom.migrate(dest, 0, None, None, 0)
    except libvirt.libvirtError as e:
        printer.puts("Controler - migrate: libvirtError", True)  
        raise

    printer.puts('Dominio ' + new_dom.name() + '  was migrated.')

    return new_dom

def scale(dom, vcpuNumber, memNumber):
    try:
       scaleVcpu(dom, vcpuNumber)
       scaleMemory(dom, memNumber)        
    except libvirt.libvirtError as e:
        printer.puts("Controler - scale: libvirtError", True)  
        raise
    
def scaleVcpu(dom, vcpuNumber):
    try:
        dom.setVcpusFlags(nvcpus=vcpuNumber, flags=libvirt.VIR_DOMAIN_VCPU_GUEST)
    except libvirt.libvirtError as e:
        printer.puts("Controler - scale vcpu: libvirtError", True)  
        raise
    
def scaleMemory(dom, memNumber):
    try:
        dom.setMemoryFlags(memory=memNumber, flags=libvirt.VIR_DOMAIN_VCPU_GUEST)
    except libvirt.libvirtError as e:
        printer.puts("Controler - scale memory: libvirtError", True)  
        raise
    
def manager_app(app):
    app.execApp()


def execThread(app):
    t1 = Commom.FuncThread(manager_app, app)
    t1.start()

    return t1

def runTestMigrate():
    status = True
    
    try:
        src = connect2Host(hosts_info["src"])
        dest = connect2Host(hosts_info["dest"])

        dom = startDom(guest_info["name"], src)


        app = RemoteApp(printer, app_info, guest_info)
        
        # start new thread and exec application
        thread1 = execThread(app)

        if config["migrate"]:
            time.sleep(int(migration_info["waiting"]))
            dom = migrate(src, dest, dom)

        thread1.join()

        out, err, code, runtime = app.getAppOutput()

        if code == 0:
            printer.puts("Application Finished with sucess")
            printer.puts("application runtime: " + str(runtime))

        else:
            printer.puts("Application Finished with error", True)
            printer.puts(err, True)
            printer.puts(out, True)
            print "Erro code: ", code



        # output csv
        if config["csv"]:
            with open(csv_info["path"]+csv_info["name"], "a") as csv:
                csv.write(str(runtime) + "\n")

        # close environment
        destroyDom(dom)
        src.close()
        dest.close()
        app.closeSSH()
        
def runTestScale():
    status = True
    
    try:
        src = connect2Host(hosts_info["src"])
        dest = connect2Host(hosts_info["dest"])

        dom = startDom(guest_info["name"], src)
#        app = RemoteApp(printer, app_info, guest_info)
        
        # start new thread and exec application
#       thread1 = execThread(app)

        scale(dom, 3, 2000)

        #thread1.join()

        out, err, code, runtime = app.getAppOutput()

        if code == 0:
            printer.puts("Application Finished with sucess")
            printer.puts("application runtime: " + str(runtime))

        else:
            printer.puts("Application Finished with error", True)
            printer.puts(err, True)
            printer.puts(out, True)
            print "Erro code: ", code



        # output csv
        if config["csv"]:
            with open(csv_info["path"]+csv_info["name"], "a") as csv:
                csv.write(str(runtime) + "\n")

        # close environment
        # destroyDom(dom)
        src.close()
        dest.close()
        app.closeSSH()


    except Exception as e:
        printer.puts("ERROR: main test error", True)
        status = False
        print e
        traceback.print_exc()

    return status
    

def forceDestroyDom():
    printer.puts("Forcing close environment!", True)
    try:
        # get the environment
        src = connect2Host(hosts_info["src"])
        dest = connect2Host(hosts_info["dest"])

        dom_src = getDomByName(guest_info["name"], src)
        dom_dest = getDomByName(guest_info["name"], dest)

        if dom_src is not None:
            destroyDom(dom_src)
        if dom_dest is not None:
            destroyDom(dom_dest)        
        
    except:
        print "error to close the environment"


def migration():
    msg = '''
    '''
    print_testInfo()

    num_executions = 1
    if config["repeat"]:
        num_executions = int(app_info["repeat"])

    for i in range(num_executions):

        printer.puts("Controle: running test " + str(i+1))

        testSuccess = runTest()

        if testSuccess and config["mailme"]:
            mail.send_email(subject="Success: " + csv_info["name"])
        
        elif not testSuccess:
            if config["mailme"]:
                mail.send_email_warning(subject="Error: " + csv_info["name"], body="Error test " + str(i+1))

            forceDestroyDom()

        printer.puts("###########\n\n")

def scaling():
    
    pass




def main():
    # TODO print test info

    # print_testInfo()

    if action['type'] == "migration":
        migration()
    elif action['type'] == "scaling":
        scaling()
    

if __name__ == "__main__":
    main()