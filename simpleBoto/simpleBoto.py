#! /usr/bin/python


import time
import paramiko

import boto3
from botocore.exceptions import ClientError, ConfigParseError

class simpleBoto:

    def __init__(self, printer, ec2_info, app_info):
        print "init simpleBoto"

        self.auth_timeout = int(app_info["auth_timeout"])
        self.ssh_repeat = int(app_info["ssh_repeat"])
        
        # ec2 info
        self.ami = ec2_info["ami"]
        self.security_groups = ec2_info["security_groups"]
        self.key_name = ec2_info["key_name"]
        self.key_location = ec2_info["ssh_key_file"]
        self.start_type = ec2_info["start_type"]
        self.user = ec2_info["user"]
        self.port = int(ec2_info["port"])
        self.verbose = False
        
        
        print "Imagem:"+self.ami+"Grupo:"+self.security_groups+"Key:"+self.key_name
        # connection info
        # self.ip = guest_info["ip"]
        
        # self.pwd = guest_info["password"]
        


        try:
            self.ec2 = boto3.resource("ec2")
            self.ec2_client = boto3.client("ec2")
            print "Acesso EC2 Criado com sucesso"
        except ClientError as e:
            print e
            raise

        # print self.ip, self.user, self.pwd, self.port

        self.printer = printer
    
    def wait4Connection(self, ssh_repeat,instance):
        count = 0
        
        print "Connect to:" + instance.id
        while count < ssh_repeat:
            time.sleep(1)
            try:
                ip = instance.public_dns_name
                self.client = paramiko.SSHClient()
                self.client.load_system_host_keys()
                self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                self.client.connect(hostname=ip, port=self.port, username=self.user,  auth_timeout=self.auth_timeout,key_filename=self.key_location )
                count = ssh_repeat
            except Exception as e:
                print e, "try number " + str(count + 1)
                count += 1

        try:
            transport = self.client.get_transport()
            transport.send_ignore()
            
        except Exception as e:
            self.printer.puts("SSH connection to " + str(ip) + " error ", True)
            raise
        self.printer.puts("SSH connection success")
        self.client.close()


    def create_instances(self, instance_type=None, minCount=1, maxCount=1, wait=True):        
        """
        :param instance_type: str
        :param minCount: int 
        :param maxCount: int
        :return: list
        """

        # print self.ami, self.default_type, self.security_groups, self.key_name, minCount, maxCount
        print "init simpleBoto"
        try:

            if instance_type is None:
                instance_type = self.start_type

            new_instances = self.ec2.create_instances(ImageId=self.ami, InstanceType=instance_type,
                                                             SecurityGroupIds=[self.security_groups], KeyName=self.key_name,
                                                             MinCount=minCount,
                                                             MaxCount=maxCount)
        except ClientError as e:
            print e
            raise

        self.printer.puts("### New Instances: ###")

        instances_id = []

        for instance in new_instances:
            instances_id.append(instance.id)
            self.printer.puts(instance.id + " " + instance.instance_type)
            if wait:
                instance.wait_until_running()
                instance.load()
                
        return new_instances

    """
    get one instance
    """
    def get_instance(self, id):
        """
        :param id: string
        :return: EC2.Instance
        """
        try:
            instance = self.ec2.Instance(id)

        except ClientError as e:
            print e
            raise

        return instance

    """
    get instances based on de state
    """
    def get_instances(self, values=["running"]):
        # create filter for instances in running state
        filters = [
            {
                'Name': 'instance-state-name',
                'Values': values
            }
        ]

        # filter the instances based on filters() above
        instances = self.ec2.instances.filter(Filters=filters)

        instances_id = []

        for instance in instances:
            self.printer.puts(instance.id + " " + instance.state["Name"])
            instances_id.append(instance.id)

        return instances

    def get_boto():
        return boto3.resource('ec2')
  
    def terminate_all_instances(self, wait=True):
        instances = self.get_instances(values=["running", "stopped"])

        try:
            instances.terminate()
        except ClientError as e:
            print e
            raise

        self.printer.puts("Terminating all instances...")
        for instance in instances:
            self.printer.puts(instance.id + " " + instance.instance_type)
            if wait:
                instance.wait_until_terminated()



    def terminate_instance(self, id, wait=True):
        instance = self.get_instance(id)

        try:
            self.printer.puts("terminating instance: " + instance.id + " " + instance.instance_type)
            instance.terminate()
        except ClientError as e:
            print e
            raise

        if wait:
            instance.wait_until_terminated()



    def get_instances(self, filters=[], InstanceIds=[]):
        try:
            response = self.ec2_client.describe_instances(Filters=filters, InstanceIds=InstanceIds)
        except ClientError as e:
            print e
            return

        ec2_resource = boto3.resource('ec2')

        instances = []

        # get all instance ids
        for reservationInfo in response['Reservations']:
            for instanceInfo in reservationInfo['Instances']:
                instances.append(ec2_resource.Instance(instanceInfo['InstanceId']))

        return instances


    def stop_instances(self, instance):
        """
        :type self.ec2_client: pyboto3.ec2
        :type instance_ids: list[str]
            :return:
        """

        #filter = [
            #{'Name': 'instance-state-name',
            #'Values': ['running']}
            #]

        #running_instances = self.get_instances(self, filters=filter, InstanceIds=instance_ids)

        #if not running_instances:
            #return

        #for vm in running_instances:
            #self.log_print("Stopping: " + vm.id)
        instance.stop()


    def start_instances(self, instance):
        """
        :type self.ec2_client: pyboto3.ec2
        :type instance_ids: list[str]
        :return:
        """
        
        

        try:
            instance.start()
        except ClientError as e:
            print e
            return 

    def make_vertical_migration(self, instance, new_type):
        """
        :type self.ec2_client: pyboto3.ec2
        :type instances_id: list[str]]
        :type new_type: str
        :return:
        """

        print "Make Vertical Scaling"

        # waiters filter
        filter = [
            {'Name': 'instance-id',
            'Values': [instance.id]}
        ]

        # get instances
        vms = instance

        if not vms:
            return

        # check if instances have a different type
        #for i in range(len(vms)):
            #if vms[i].instance_type == new_type:
                #self.log_print("Instance " + vms[i].id + "" \
                #" : The Vertical Migration will not be executed for this instance\n" \
                #" old_type and new_type are equal")

                ## remove instance from the list
                #del vms[i]


        # build boto3 waiters
        waiter_stopped = self.ec2_client.get_waiter('instance_stopped')
        waiter_running = self.ec2_client.get_waiter('instance_running')



        # start time of the migration
        

        #self.log_print("stopping vms...")
        # stopping vms
        print "Stop VM"
        self.stop_instances(instance)

        # wait until vms is completely stopped
        waiter_stopped.wait(Filters=filter)

        
        print "Stoped VM"
        try:
            #for vm in vms:
                # update vm information
            vms.reload()
            #self.log_print("Change vm: " + vms.id + "  " + vms.instance_type + " to " + new_type)
                # Do vertical migration
            vms.modify_attribute(InstanceType={'Value': new_type})
                # start vm
        except ClientError as e:
            print e
            return
        print "Start VM"
        self.start_instances(instance)
        #self.log_print("starting vms...")
        # wait until vm is running
        waiter_running.wait(Filters=filter)

        print "Started VM"

        #for vm in vms:
        vms.reload
        #print vms.public_dns_name + "@" + str(lap1-start_time) + "@" + str(stop-lap1)


        # print "Vertical Migration finished.\n" \
        #       "Stopping time:", lap1 - start_time, "\n" \
        #       "Starting time:", stop - lap1,  "\n" \
        #       "Migration Total Time(s):", stop - start_time,  "\n" + 10*"*"
    
    def print_all_instances():
        instances = get_instances()

        if not instances:
            return

        for vm in instances:
            print vm.id + " " +  vm.instance_type + " " +  vm.state['Name']


    def log_print(msg):
        if self.verbose:
            print msg
