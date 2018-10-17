#! /usr/bin/python

import time


import boto3
import botocore
import paramiko


class remoteApp:

    def __init__(self, printer, app_info, ec2_info, instance=None):
        # app info
        self.command = app_info["command"]
        self.app_path = app_info["path"]

        self.auth_timeout = int(app_info["auth_timeout"])

        # connection info

        while instance.public_ip_address is None:
            printer.puts("waiting public ip...")
            time.sleep(3)
            instance.load()

        self.ip = instance.public_ip_address
        self.user = ec2_info["user"]
        self.key_file = ec2_info["ssh_key_file"]
        self.port = int(ec2_info["port"])

        self.ssh_repeat = app_info["ssh_repeat"]

        # print self.ip, self.user, self.pwd, self.port

        self.printer = printer

        # self.ssh_repeat = int(app_info["ssh_repeat"])

        self.instance = instance

        # start connection
        self.__openSSH()

    def __openSSH(self):

        # start connection
        # for i in range(self.repeat):

        print self.ip, self.port, self.user

        count = 0
        while count < self.ssh_repeat:
            time.sleep(1)
            try:

                key = paramiko.RSAKey.from_private_key_file(self.key_file)
                self.client = paramiko.SSHClient()
                self.client.load_system_host_keys()
                self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

                self.client.connect(hostname=self.ip, port=self.port, username=self.user, pkey=key,
                                    auth_timeout=self.auth_timeout)
                count = self.ssh_repeat
            except Exception as e:
                print e, "try number " + str(count + 1)
                count += 1

        try:
            transport = self.client.get_transport()
            transport.send_ignore()
        except Exception as e:
            self.printer.puts("SSH connection to " + self.ip + " error ", True)
            raise


    def closeSSH(self):
        try:
            self.client.close()
        except:
            self.printer.puts("Close SSH connection error", True)

        self.printer.puts("Close ssh connection.")

    # Start the App and wait until finish
    def execApp(self):

        if self.appIsRunning():
            self.printer.puts("ExecApp Error: App is alredy running.", True)
            return

        try:
            self.ssh_transp = self.client.get_transport()
            self.chan = self.ssh_transp.open_session()

            self.chan.setblocking(0)

            start_time = time.time()
            print "execapp: " + self.app_path + self.command
            self.chan.exec_command(self.app_path + self.command)

            self.printer.puts("execApp: waiting...")
            while not self.chan.exit_status_ready():
                # time.sleep(sleeptime)
                pass

            end_time = time.time()

            self.runtime = end_time - start_time

        # self.stdin, self.stdout, self.stderr = self.client.exec_command(self.app_path+self.command)
        except:
            self.printer.puts("Error: execApp except: " + self.app_path + self.command, True)
            raise

        self.printer.puts("ExecApp: app finished.")

    def getAppOutput(self):

        outdata = ""
        errdata = ""
        sleeptime = 0.001  # TODO add in controler.conf

        # check if the output is alredy on the class
        # and if app was started
        try:
            if not self.ssh_transp.isAlive() and hasattr(self, 'app_output'):
                return self.app_output, self.app_err, self.app_exitCode, self.runtime
        except AttributeError:
            self.printer.puts("Error: getAppOutput app was not started")
            raise

        try:
            while True:
                while self.chan.recv_ready():
                    outdata += self.chan.recv(1000)
                while self.chan.recv_stderr_ready():
                    errdata += self.chan.recv_stderr(1000)
                if self.chan.exit_status_ready():
                    break

            retcode = self.chan.recv_exit_status()
            self.ssh_transp.close()

        except:
            self.printer.puts("Error: getAppOutput except", True)
            raise

        # update global vars
        self.app_output = outdata
        self.app_err = errdata
        self.app_exitCode = retcode

        return outdata, errdata, retcode, self.runtime

    def appIsRunning(self):

        try:
            status = not self.chan.exit_status_ready()
        except AttributeError:
            status = False

        # if exit_status is true: app is not running
        return status
