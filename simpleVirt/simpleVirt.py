#! /usr/bin/python


import libvirt


class simpleVirt:

    def __init__(self, printer, hosts_info, guest_info):

        self.printer = printer
        self.hosts_info = hosts_info
        self.guest_info = guest_info

    def connect2Host(self, host):
        conn = libvirt.open('qemu+ssh://' + host + '/system')
        if conn == None:
            self.printer.puts('Failed to connect to the hypervizor', True)
        else:
            self.printer.puts('Qemu Connected to ' + host)

        return conn

    def getDomByName(self, name, conn):

        try:
            dom = conn.lookupByName(name)

        except libvirt.libvirtError:
            self.printer.puts('Dominio ' + name + ' was not defined.')
            return None

        return dom

    def startDom(self, name, conn):
        try:
            dom = self.getDomByName(name, conn)
            dom.create()
        except libvirt.libvirtError as e:
            self.printer.puts("Controler - startDom: libvirtError", True)
            raise

        self.printer.puts('Dominio ' + name + ' was started.')
        return dom

    def destroyDom(self, dom):
        try:
            dom.destroy()
        except libvirt.libvirtError as e:
            self.printer.puts("Controler - destroyDom: libvirtError", True)
            return None

        self.printer.puts('Dominio  was destroyed.')
        return dom

    def migrate(self, src, dest, dom):
        try:
            new_dom = dom.migrate(dest, 0, None, None, 0)
        except libvirt.libvirtError as e:
            self.printer.puts("Controler - migrate: libvirtError", True)
            raise

        self.printer.puts('Dominio ' + new_dom.name() + '  was migrated.')

        return new_dom

    def scale(self, dom, vcpuNumber, memNumber):
        try:
            self.scaleVcpu(dom, vcpuNumber)
            self.scaleMemory(dom, memNumber)
        except libvirt.libvirtError as e:
            self.printer.puts("Controler - scale: libvirtError", True)
            raise

    def scaleVcpu(self, dom, vcpuNumber):
        try:
            currentVcpuCount = self.getVcpuCount(dom)
            
            if vcpuNumber < currentVcpuCount :
            
                dom.setVcpusFlags(nvcpus=vcpuNumber, flags=libvirt.VIR_DOMAIN_VCPU_GUEST)
                
            elif vcpuNumber > currentVcpuCount:
                dom.setVcpus(nvcpus=vcpuNumber)
                #dom.setVcpusFlags(nvcpus=vcpuNumber, flags=libvirt.VIR_DOMAIN_AFFECT_LIVE)
                dom.setVcpusFlags(nvcpus=vcpuNumber, flags=libvirt.VIR_DOMAIN_AFFECT_CONFIG)
                dom.setVcpusFlags(nvcpus=vcpuNumber, flags=libvirt.VIR_DOMAIN_VCPU_GUEST)
                
                
                
                
        except libvirt.libvirtError as e:
            self.printer.puts("Controler - scale vcpu: libvirtError", True)
            raise

    def scaleMemory(self, dom, memNumber):
        try:
            dom.setMemoryFlags(
                memory=memNumber, flags=libvirt.VIR_DOMAIN_VCPU_GUEST)
        except libvirt.libvirtError as e:
            self.printer.puts("Controler - scale memory: libvirtError", True)
            raise
        
    def getVcpuCount(self, dom):
        try:
            return dom.vcpusFlags(libvirt.VIR_DOMAIN_VCPU_GUEST)
        except libvirt.libvirtError as e:
            self.printer.puts("Controler - vcpuCount: libvirtError", True)
            raise
    
        
    def forceDestroyDom(self):
        self.printer.puts("An error occured. Finishing environment...", True)
        try:
            # get the environment
            src = self.connect2Host(self.hosts_info["src"])
            dest = self.connect2Host(self.hosts_info["dest"])

            dom_src = self.getDomByName(self.guest_info["name"], src)
            dom_dest = self.getDomByName(self.guest_info["name"], dest)

            if dom_src is not None:
                self.destroyDom(dom_src)
            if dom_dest is not None:
                self.destroyDom(dom_dest)
        except:
            self.printer.puts(
                "Warning. Check if the environment was finisshed correctly.", True)


# def runTestScale():
#     status = True
#     try:
#         src = connect2Host(hosts_info["src"])
#         dest = connect2Host(hosts_info["dest"])

#         dom = startDom(guest_info["name"], src)
#         # app = RemoteApp(printer, app_info, guest_info)

#         # start new thread and exec application
#         # thread1 = execThread(app)

#         scale(dom, 3, 2000)

#         #thread1.join()

#         out, err, code, runtime = app.getAppOutput()

#         if code == 0:
#             printer.puts("Application Finished with sucess")
#             printer.puts("application runtime: " + str(runtime))

#         else:
#             printer.puts("Application Finished with error", True)
#             printer.puts(err, True)
#             printer.puts(out, True)
#             print "Erro code: ", code


#         # output csv
#         if config["csv"]:
#             with open(csv_info["path"]+csv_info["name"], "a") as csv:
#                 csv.write(str(runtime) + "\n")

#         # close environment
#         # destroyDom(dom)
#         src.close()
#         dest.close()
#         app.closeSSH()
#     except Exception as e:
#         printer.puts("ERROR: main test error", True)
#         status = False
#         print e
#         traceback.print_exc()

#     return status


# def scaling():
#     runTestScale()
