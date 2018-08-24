#! /usr/bin/python

import libvirt
import time
import paramiko

import boto3
from botocore.exceptions import ClientError, ConfigParseError


class simpleVirt:

    # KVM FUNCTIONS
    def __init__(self, printer, hosts_info, guest_info, app_info):
        self.printer = printer
        self.hosts_info = hosts_info
        self.guest_info = guest_info

        self.auth_timeout = int(app_info["auth_timeout"])
        self.ssh_repeat = int(app_info["ssh_repeat"])

        # connection info
        self.ip = guest_info["ip"]
        self.user = guest_info["user"]
        self.pwd = guest_info["password"]
        self.port = int(guest_info["port"])

        # print self.ip, self.user, self.pwd, self.port

        self.printer = printer

    def connect2Host(self, host):
        conn = libvirt.open('qemu+ssh://' + host + '/system')
        if conn == None:
            self.printer.puts('Failed to connect to the hypervizor', True)
        else:
            self.printer.puts('Qemu Connected to ' + host)

        return conn

    def wait4Connection(self, ssh_repeat):
        count = 0

        while count < ssh_repeat:
            time.sleep(1)
            try:
                self.client = paramiko.SSHClient()
                self.client.load_system_host_keys()
                self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                self.client.connect(hostname=self.ip, port=self.port, username=self.user, password=self.pwd,
                                    auth_timeout=self.auth_timeout)
                count = ssh_repeat
            except Exception as e:
                print
                e, "try number " + str(count + 1)
                count += 1

        try:
            transport = self.client.get_transport()
            transport.send_ignore()
        except Exception as e:
            self.printer.puts("SSH connection to " + self.guest_info["ip"] + " error ", True)
            raise
        self.printer.puts("SSH connection success")
        self.client.close()

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

            info = dom.info()

            if vcpuNumber < currentVcpuCount:

                dom.setVcpusFlags(nvcpus=vcpuNumber, flags=libvirt.VIR_DOMAIN_VCPU_GUEST)

            elif vcpuNumber > currentVcpuCount:
                dom.setVcpus(nvcpus=vcpuNumber)
                # dom.setVcpusFlags(nvcpus=vcpuNumber, flags=libvirt.VIR_DOMAIN_AFFECT_LIVE)
                dom.setVcpusFlags(nvcpus=vcpuNumber, flags=libvirt.VIR_DOMAIN_AFFECT_CONFIG)
                dom.setVcpusFlags(nvcpus=vcpuNumber, flags=libvirt.VIR_DOMAIN_VCPU_GUEST)



        except libvirt.libvirtError as e:
            self.printer.puts("Controler - scale vcpu: libvirtError", True)
            raise

    def getMemoryInfo(self, dom, flag=0):
        try:
            info = dom.info()
            if (flag == 0):
                return info[1]  # RETURNS MAX MEMORY
            elif (flag == 1):
                return info[2]  # RETURNS VIRTUAL MEMORY
        except libvirt.libvirtError as e:
            self.printer.puts("Controler - scale memory: libvirtError", True)
            raise

    def scaleMemory(self, dom, memNumber):
        memNumber = memNumber * (1048576)

        try:
            if (memNumber > self.getMemoryInfo(dom, 0)):
                self.printer.puts(
                    "Controler - scale memory: memory requested is higher than the maximum memory allowed", True)
            else:
                dom.setMemory(
                    memory=memNumber)
                ballooningProc = True
                memNow = self.getMemoryInfo(dom, 1)

                while (ballooningProc):
                    time.sleep(1)
                    memNew = self.getMemoryInfo(dom, 1)
                    if (memNow < memNew):
                        memNow = memNew
                    elif (memNow == memNew):
                        ballooningProc = False
                    elif (memNow > memNew):
                        memNow = memNew

        except libvirt.libvirtError as e:
            self.printer.puts("Controler - scale memory: libvirtError", True)
            raise

    def getVcpuCount(self, dom):
        try:
            return dom.vcpusFlags(libvirt.VIR_DOMAIN_VCPU_GUEST)

        except libvirt.libvirtError as e:
            self.printer.puts("Controler - vcpuCount: libvirtError", True)
            raise

    def config(self, dom, vcpuNumber, memNumber, memMax):
        memNumber = memNumber * (1048576)
        memMax = memMax * (1048576)
        try:
            info = dom.info()
            print
            info[0]
            if (info[0] == 5):

                dom.setVcpusFlags(nvcpus=vcpuNumber, flags=libvirt.VIR_DOMAIN_AFFECT_CONFIG)
                # dom.setVcpusFlags(nvcpus=vcpuNumber, flags=libvirt.VIR_DOMAIN_AFFECT_LIVE)
                # dom.setVcpusFlags(nvcpus=vcpuNumber, flags=libvirt.VIR_DOMAIN_VCPU_MAXIMUM)
                dom.setMemoryFlags(memory=memMax, flags=libvirt.VIR_DOMAIN_MEM_MAXIMUM)
                dom.setMemoryFlags(memory=memNumber, flags=libvirt.VIR_DOMAIN_AFFECT_CONFIG)

                ballooningProc = True
                memNow = self.getMemoryInfo(dom, 1)

                while (ballooningProc):
                    time.sleep(1)
                    memNew = self.getMemoryInfo(dom, 1)
                    if (memNow < memNew):
                        memNow = memNew
                    elif (memNow == memNew):
                        ballooningProc = False
                    elif (memNow > memNew):
                        memNow = memNew
            else:
                self.printer.puts(
                    "Controler - configuration error: machine is not shutdown, cannot configurations won't take effect and maxmemory can't be changed while running",
                    True)

        except libvirt.libvirtError as e:
            self.printer.puts("Controler - configuration error: libvirtError", True)
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
                "Warning. Check if the environment was finished correctly.", True)

    #