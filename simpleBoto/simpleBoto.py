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
        self.default_type = ec2_info["default_type"]

        # connection info
        # self.ip = guest_info["ip"]
        # self.user = guest_info["user"]
        # self.pwd = guest_info["password"]
        # self.port = int(guest_info["port"])


        try:
            self.ec2 = boto3.resource("ec2")
        except ClientError as e:
            print e
            raise


        # print self.ip, self.user, self.pwd, self.port

        self.printer = printer



    # def connect2Host(self, host):
    #     conn = libvirt.open('qemu+ssh://' + host + '/system')
    #     if conn == None:
    #         self.printer.puts('Failed to connect to the hypervizor', True)
    #     else:
    #         self.printer.puts('Qemu Connected to ' + host)
    #
    #     return conn
    #
    # def wait4Connection(self, ssh_repeat):
    #     count = 0
    #
    #     while count < ssh_repeat:
    #         time.sleep(1)
    #         try:
    #             self.client = paramiko.SSHClient()
    #             self.client.load_system_host_keys()
    #             self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #             self.client.connect(hostname=self.ip, port=self.port, username=self.user, password=self.pwd,
    #                                 auth_timeout=self.auth_timeout)
    #             count = ssh_repeat
    #         except Exception as e:
    #             print
    #             e, "try number " + str(count + 1)
    #             count += 1
    #
    #     try:
    #         transport = self.client.get_transport()
    #         transport.send_ignore()
    #     except Exception as e:
    #         self.printer.puts("SSH connection to " + self.guest_info["ip"] + " error ", True)
    #         raise
    #     self.printer.puts("SSH connection success")
    #     self.client.close()
    #
    # def getDomByName(self, name, conn):
    #     try:
    #         dom = conn.lookupByName(name)
    #
    #     except libvirt.libvirtError:
    #         self.printer.puts('Dominio ' + name + ' was not defined.')
    #         return None
    #
    #     return dom
    #

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
                instance_type = self.default_type

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

        return new_instances, instances_id

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


    """
    terminate all instances (running or stopped one)
    """
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






    # AWS
    # FUNCTIONS
    #
    #
    # def get_ec2():
    #     return boto3.client("ec2")
    #
    #
    # def make_vertical_migration(self, ec2_client, instances_id, new_type):
    #     global verbose
    #     """
    #     :type ec2_client: pyboto3.ec2
    #     :type instances_id: list[str]]
    #     :type new_type: str
    #     :return:
    #     """
    #
    #     # waiters filter
    #     filter = [
    #         {'Name': 'instance-id',
    #          'Values': instances_id}
    #     ]
    #
    #     # get instances
    #     vms = self.get_instances(ec2_client, InstanceIds=instances_id)
    #
    #     if not vms:
    #         return
    #
    #     # check if instances have a different type
    #     for i in range(len(vms)):
    #         if vms[i].instance_type == new_type:
    #             self.log_print("Instance " + vms[i].id + "" \
    #                                                      " : The Vertical Migration will not be executed for this instance\n" \
    #                                                      " old_type and new_type are equal", verbose)
    #
    #             # remove instance from the list
    #             del vms[i]
    #
    #     # build boto3 waiters
    #     waiter_stopped = ec2_client.get_waiter('instance_stopped')
    #     waiter_running = ec2_client.get_waiter('instance_running')
    #
    #     # start time of the migration
    #     start_time = timeit.default_timer()
    #
    #     self.log_print("stopping vms...", verbose)
    #     # stopping vms
    #     self.stop_instances(ec2_client, instances_id)
    #
    #     # wait until vms is completely stopped
    #     waiter_stopped.wait(Filters=filter)
    #
    #     lap1 = timeit.default_timer()
    #
    #     try:
    #         for vm in vms:
    #             # update vm information
    #             vm.reload()
    #             self.log_print("Change vm: " + vm.id + "  " + vm.instance_type + " to " + new_type, verbose)
    #             # Do vertical migration
    #             vm.modify_attribute(InstanceType={'Value': new_type})
    #             # start vm
    #     except ClientError as e:
    #         print
    #         e
    #         return
    #
    #     self.start_instances(ec2_client, instances_id)
    #     self.log_print("starting vms...", verbose)
    #     # wait until vm is running
    #     waiter_running.wait(Filters=filter)
    #
    #     stop = timeit.default_timer()
    #
    #     for vm in vms:
    #         vm.reload
    #         print
    #         vm.public_dns_name + "@" + str(lap1 - start_time) + "@" + str(stop - lap1)
    #
    #     # print "Vertical Migration finished.\n" \
    #     #       "Stopping time:", lap1 - start_time, "\n" \
    #     #       "Starting time:", stop - lap1,  "\n" \
    #     #       "Migration Total Time(s):", stop - start_time,  "\n" + 10*"*"
    #
    #
    # def create_vms(self, ec2_client, image_id, how_many, instance_type='t2.micro'):
    #     global verbose
    #
    #     waiter_running = ec2_client.get_waiter('instance_running')
    #
    #     start = timeit.default_timer()
    #
    #     instances = self.create_instances(image_id, instanceType=instance_type, minCount=how_many, maxCount=how_many)
    #
    #     if not instances:
    #         return
    #
    #     ids = []
    #
    #     for vm in instances:
    #         ids.append(vm.id)
    #
    #     # waiters filter
    #     filter = [ # def startDom(self, name, conn):
    #     try:
    #         dom = self.getDomByName(name, conn)
    #         dom.create()
    #     except libvirt.libvirtError as e:
    #         self.printer.puts("Controler - startDom: libvirtError", True)
    #         raise
    #
    #     self.printer.puts('Dominio ' + name + ' was started.')
    #     return dom
    #         {'Name': 'instance-id',
    #          'Values': ids}
    #     ]
    #
    #     self.log_print("waiting instances...", verbose)
    #     waiter_running.wait(Filters=filter)
    #     self.log_print("Instances is running...", verbose)
    #
    #     end = timeit.default_timer()
    #
    #     # print "create time (s): ", end - start
    #     # print "num_vms: ", len(instances)
    #
    #     return instances, end - start
    #
    #
    # def get_instances(self, ec2_client, filters=[], InstanceIds=[]):
    #     try:
    #         response = ec2_client.describe_instances(Filters=filters, InstanceIds=InstanceIds)
    #     except ClientError as e:
    #         print
    #         e
    #         return
    #     """
    #     :type ec2_client: pyboto3.ec2
    #     :return: pyboto3.Ec2.Instance
    #     """
    #
    #     ec2_resource = boto3.resource('ec2')
    #
    #     instances = []
    #
    #     # get all instance ids
    #     for reservationInfo in response['Reservations']:
    #         for instanceInfo in reservationInfo['Instances']:
    #             instances.append(ec2_resource.Instance(instanceInfo['InstanceId']))
    #
    #     return instances
    #
    #
    # def stop_instances(self, ec2_client, instance_ids=[], verbose=False):
    #     """
    #     :type ec2_client: pyboto3.ec2
    #     :type instance_ids: list[str]
    #     :return:
    #     """
    #
    #     filter = [
    #         {'Name': 'instance-state-name',
    #          'Values': ['running']}
    #     ]
    #
    #     running_instances = self.get_instances(ec2_client, filters=filter, InstanceIds=instance_ids)
    #
    #     if not running_instances:
    #         return
    #
    #     for vm in running_instances:
    #         self.log_print("Stopping: " + vm.id, verbose)
    #         vm.stop()
    #
    #
    # def start_instances(self, ec2_client, instance_ids=[], verbose=False):
    #     """
    #     :type ec2_client: pyboto3.ec2
    #     :type instance_ids: list[str]
    #     :return:
    #     """
    #
    #     filter = [
    #         {'Name': 'instance-state-name',
    #          'Values': ['stopped']}
    #     ]
    #
    #     running_instances = self.get_instances(ec2_client, filters=filter, InstanceIds=instance_ids)
    #
    #     if not running_instances:
    #         return
    #
    #     try:
    #         for vm in running_instances:
    #             self.log_print("Starting: " + vm.id, verbose)
    #             vm.start()
    #     except ClientError as e:
    #         print
    #         e
    #         return
    #
    #
    # def terminate_instances(self, ec2_client, InstanceIds=[], verbose=False):
    #     '''
    #     :type ec2_client: pyboto3.ec2
    #     :return:
    #     '''
    #
    #     filter = [
    #         {'Name': 'instance-state-name',
    #          'Values': ['running', 'stopped']}
    #     ]
    #
    #     instances = self.get_instances(ec2_client, filters=filter, InstanceIds=InstanceIds)
    #
    #     if not instances:
    #         return
    #     instances_ids = []
    #     for vm in instances:
    #         self.log_print("Terminating: " + vm.id, verbose)
    #         vm.terminate()
    #         instances_ids.append(vm.id)
    #
    #     waiter = ec2_client.get_waiter('instance_terminated')
    #     waiter.wait(InstanceIds=instances_ids)
    #
    #
    # def create_instances(self, imageId, instanceType, securityGroups=['launch-wizard-2'], keyName='ec2', minCount=1,
    #                      maxCount=1, verbose=False):
    #     """
    #     :type imageId:      str
    #     :type instanceType: str
    #     :type securityGroups: list[str]
    #     :type keyName: str
    #     :type minCount: int
    #     :type maxCount: int
    #     :return: list
    #     """
    #
    #     ec2_resorce = boto3.resource("ec2")
    #
    #     try:
    #         new_instances = ec2_resorce.create_instances(ImageId=imageId, InstanceType=instanceType,
    #                                                      SecurityGroups=securityGroups, KeyName=keyName,
    #                                                      MinCount=minCount,
    #                                                      MaxCount=maxCount)
    #     except ClientError as e:
    #         print
    #         e
    #         return
    #
    #     log_print("### New Instances: ###", verbose)
    #
    #     for vm in new_instances:
    #         self.log_print(vm.id + " " + vm.public_dns_name, verbose)
    #
    #     return new_instances
    #
    #
    # def log_print(self, msg, verbose):
    #     if verbose:
    #         print
    #         msg
