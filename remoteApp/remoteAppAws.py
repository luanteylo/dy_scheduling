#! /usr/bin/python

import time


import paramiko

EXECUTE_COMMAND_1 = 0
EXECUTE_COMMAND_2 = 1

 
class remoteAppAws:
 
    def __init__(self, printer, app_info, ec2_info, access, command):
            # app info
            if  command == EXECUTE_COMMAND_1:
                self.command = app_info["command1"]
            elif command == EXECUTE_COMMAND_2:
                self.command = app_info["command2"]
            self.command_compile = app_info["command_compile"]
            self.app_path = app_info["path"]
            self.auth_timeout = int(app_info["auth_timeout"])
            self.ssh_repeat = int(app_info["ssh_repeat"])
		
		
            # connection info
            self.ip = access
            self.user = ec2_info["user"]
            self.port = int(ec2_info["port"])
            self.key_location = ec2_info["ssh_key_file"]
            self.exec_file = ec2_info["exec_file"]
            self.runner_file = ec2_info["runner_file"]
            # print self.ip, self.user, self.pwd, self.port
 
            self.printer = printer
            self.ssh_repeat = int(app_info["ssh_repeat"])
 
            #start connection
 
 		
            self.__openSSH()
            


            
 		
 
    def __openSSH(self):
            #start connection
 		# for i in range(self.repeat):
 		
            count = 0
            while count < self.ssh_repeat:
                    time.sleep(1)
                    try:
                            self.client = paramiko.SSHClient()
                            self.client.load_system_host_keys()
                            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                            
                            
                            self.client.connect(hostname=self.ip, port=self.port, username=self.user,  auth_timeout=self.auth_timeout,key_filename=self.key_location )
                            self.sftp = self.client.open_sftp()
                            self.sftp.sshclient = self.client
                            
                            count = self.ssh_repeat
                    except Exception as e:
                            print e, "try number " + str(count+1)
                            count += 1
 
            try:
                    transport = self.client.get_transport()
                    transport.send_ignore()
            except Exception as e:
 	
                    self.printer.puts("SSH connection to " + str(self.ip) +  " error ", True)
                    raise
            self.printer.puts("SSH connection success")
 		
 	
    def closeSSH(self):
            try:
                    self.client.close()
            except:
                    self.printer.puts("Close SSH connection error", True)
 
            self.printer.puts("Close ssh connection.")
 
 
 	# Start the App and wait until finish
    def execApp(self):
            outdata, errdata = '', ''
            if self.appIsRunning():
                    self.printer.puts("ExecApp Error: App is alredy running.", True)
                    return
 
            try:
                    self.ssh_transp = self.client.get_transport()
                    self.chan = self.ssh_transp.open_session()
 		
                    self.chan.setblocking(0)
 			
                    start_time = time.time()
                    print "execapp: " + self.app_path+self.command
                    
                    




                    

        # Using the SSH client, create a SFTP client.
                    
        # Keep a reference to the SSH client in the SFTP client as to prevent the former from
        # being garbage collected and the connection from being closed.
                    

                    print "Send program"+ '/home/matheus/'+self.exec_file, self.app_path+self.exec_file
                    self.sftp.put('/home/matheus/'+self.exec_file, self.app_path+self.exec_file)
                    self.sftp.put('/home/matheus/'+self.runner_file, self.app_path+self.runner_file)
                    self.sftp.close()
                    print "Prepare enviroment"
                    print "Update"
                    #self.chan.exec_command("sudo apt-get update")
                    
                    #self.printer.puts("updating apt get: waiting...")	
                    #while True:  # monitoring process
                        ## Reading from output streams
                        #print "Updating"
                        #while self.chan.recv_ready():
                            #outdata += self.chan.recv(1000)
                        #while self.chan.recv_stderr_ready():
                            #errdata += self.chan.recv_stderr(1000)
                        #if self.chan.exit_status_ready():  # If completed
                            #print "Updated"
                            #break
                        #time.sleep(1)
                    #print "Prepare enviroment"
                    #print "Install"
                    #self.chan.exec_command("sudo apt-get --assume-yes install g++ libcr-dev mpich mpich-doc libpapi-dev papi-tools python2.7-dev python")
                    
                    #self.printer.puts("prepare enviroment: waiting...")	
                    #while True:  # monitoring process
                        ## Reading from output streams
                        #print "Installing"
                        #while self.chan.recv_ready():
                            #outdata += self.chan.recv(1000)
                        #while self.chan.recv_stderr_ready():
                            #self.errdata += chan.recv_stderr(1000)
                        #if self.chan.exit_status_ready():  # If completed
                            #print "Installed"
                            #break
                        #time.sleep(1)
                    
                    print "Execute compile command"+self.app_path+self.command_compile
                    self.chan.exec_command(self.command_compile)
                    
                    self.printer.puts("compile: waiting...")	
                    while not self.chan.exit_status_ready():
                            # time.sleep(sleeptime)
                            pass
                        
                    self.chan = self.ssh_transp.open_session()
 		
                    self.chan.setblocking(0)
                    
                    print "Execute command"+self.app_path+self.command
                    self.chan.exec_command(self.command)
 			
                    self.printer.puts("execApp: waiting...")	
                    while not self.chan.exit_status_ready():
                            # time.sleep(sleeptime)
                            pass
 
                    end_time = time.time()
 
                    self.runtime = end_time - start_time
 
                    #self.stdin, self.stdout, self.stderr = self.client.exec_command(self.app_path+self.command)
            except:
                    self.printer.puts("Error: execApp except: " + self.app_path+self.command, True)
                    raise
 			
 
            self.printer.puts("ExecApp: app finished.")
 
 	
    def getAppOutput(self):
 		
            outdata = ""
            errdata = ""
            sleeptime = 0.001 # TODO add in controler.conf
 
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

