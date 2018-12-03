#! /usr/bin/python

import libvirt
import time
import paramiko
import os
import boto3
from botocore.exceptions import ClientError, ConfigParseError
import googleapiclient.discovery
from six.moves import input

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
        
    def connect2Host(self, host, hypervisor):
	if(hypervisor == "kvm"):        
	    conn = libvirt.open('qemu+ssh://matheus@' + host + '/system')
	    #conn = libvirt.open('qemu://' + host + '/system')
	if(hypervisor == "virtual_box"):
	    conn = libvirt.open('vbox:///session')
        if(hypervisor == "google_cloud"):
            conn = googleapiclient.discovery.build('compute', 'v1')
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

    #AWS FUNCTIONS
    
    def get_ec2():
        return boto3.client("ec2")
        
    def make_vertical_migration(self,ec2_client, instances_id, new_type):  
        global  verbose
        """
        :type ec2_client: pyboto3.ec2
        :type instances_id: list[str]]
        :type new_type: str
        :return:
        """

    

        # waiters filter
        filter = [
            {'Name': 'instance-id',
            'Values': instances_id}
        ]

        # get instances
        vms = self.get_instances(ec2_client, InstanceIds=instances_id)

        if not vms:
            return

        # check if instances have a different type
        for i in range(len(vms)):
            if vms[i].instance_type == new_type:
                self.log_print("Instance " + vms[i].id + "" \
                " : The Vertical Migration will not be executed for this instance\n" \
                " old_type and new_type are equal", verbose)

                # remove instance from the list
                del vms[i]


        # build boto3 waiters
        waiter_stopped = ec2_client.get_waiter('instance_stopped')
        waiter_running = ec2_client.get_waiter('instance_running')



        # start time of the migration
        start_time = timeit.default_timer()

        self.log_print("stopping vms...", verbose)
        # stopping vms
        self.stop_instances(ec2_client, instances_id)

        # wait until vms is completely stopped
        waiter_stopped.wait(Filters=filter)

        lap1 = timeit.default_timer()

        try:
            for vm in vms:
                # update vm information
                vm.reload()
                self.log_print("Change vm: " + vm.id + "  " + vm.instance_type + " to " + new_type, verbose)
                # Do vertical migration
                vm.modify_attribute(InstanceType={'Value': new_type})
                # start vm
        except ClientError as e:
            print e
            return

        self.start_instances(ec2_client, instances_id)
        self.log_print("starting vms...", verbose)
        # wait until vm is running
        waiter_running.wait(Filters=filter)

        stop = timeit.default_timer()

        for vm in vms:
            vm.reload
            print vm.public_dns_name + "@" + str(lap1-start_time) + "@" + str(stop-lap1)


        # print "Vertical Migration finished.\n" \
        #       "Stopping time:", lap1 - start_time, "\n" \
        #       "Starting time:", stop - lap1,  "\n" \
        #       "Migration Total Time(s):", stop - start_time,  "\n" + 10*"*"

    def create_vms(self,ec2_client, image_id, how_many, instance_type='t2.micro'):
        waiter_running = ec2_client.get_waiter('instance_running')

        instances = self.create_instances(image_id, instanceType=instance_type, minCount=how_many, maxCount=how_many)

        if not instances:
            return

        ids = []

        for vm in instances:
            ids.append(vm.id)

        # waiters filter
        filter = [
            {'Name': 'instance-id',
            'Values': ids}
        ]
    
        self.log_print("waiting instances...", verbose)
        waiter_running.wait(Filters=filter)
        self.log_print("Instances is running...", verbose)

        # print "create time (s): ", end - start
        # print "num_vms: ", len(instances)

        return instances

    def get_instances(self,ec2_client, filters=[], InstanceIds=[]):
        try:
            response = ec2_client.describe_instances(Filters=filters, InstanceIds=InstanceIds)
        except ClientError as e:
            print e
            return
        """
        :type ec2_client: pyboto3.ec2
        :return: pyboto3.Ec2.Instance
        """

    

        ec2_resource = boto3.resource('ec2')

        instances = []

        # get all instance ids
        for reservationInfo in response['Reservations']:
            for instanceInfo in reservationInfo['Instances']:
                instances.append(ec2_resource.Instance(instanceInfo['InstanceId']))

        return instances

    def stop_instances(self,ec2_client, instance_ids=[], verbose=False):
        """
        :type ec2_client: pyboto3.ec2
        :type instance_ids: list[str]
        :return:
        """

        filter = [
            {'Name': 'instance-state-name',
            'Values': ['running']}
            ]

        running_instances = self.get_instances(ec2_client, filters=filter, InstanceIds=instance_ids)

        if not running_instances:
            return

        for vm in running_instances:
            self.log_print("Stopping: " + vm.id, verbose)
            vm.stop()

    def start_instances(self,ec2_client, instance_ids=[], verbose=False):
        """
        :type ec2_client: pyboto3.ec2
        :type instance_ids: list[str]
        :return:
        """

        filter = [
            {'Name': 'instance-state-name',
            'Values': ['stopped']}
            ]

        running_instances = self.get_instances(ec2_client, filters=filter, InstanceIds=instance_ids)

        if not running_instances:
            return

        try:
            for vm in running_instances:
                self.log_print("Starting: " + vm.id, verbose)
                vm.start()
        except ClientError as e:
            print e
            return 

    def terminate_instances(self,ec2_client, InstanceIds = [], verbose=False):
        '''
        :type ec2_client: pyboto3.ec2
        :return:
        '''

        filter = [
            {'Name': 'instance-state-name',
            'Values': ['running', 'stopped']}
        ]

        instances = self.get_instances(ec2_client, filters=filter, InstanceIds=InstanceIds)

        if not instances:
            return
        instances_ids = []
        for vm in instances:
            self.log_print("Terminating: " + vm.id, verbose)
            vm.terminate()
            instances_ids.append(vm.id)

        waiter = ec2_client.get_waiter('instance_terminated')
        waiter.wait(InstanceIds=instances_ids)

    def create_instances(self,imageId, instanceType, securityGroups=['default'],keyName='MatheusMotorhead.pem', minCount=1, maxCount=1, verbose=False):
        """
        :type imageId:      str
        :type instanceType: str
        :type securityGroups: list[str]
        :type keyName: str
        :type minCount: int
        :type maxCount: int
        :return: list
        """

        ec2_resorce = boto3.resource("ec2")

        try:
            new_instances = ec2_resorce.create_instances(ImageId=imageId, InstanceType=instanceType,
                                                    SecurityGroups=securityGroups, KeyName=keyName, MinCount=minCount,
                                                    MaxCount=maxCount)
        except ClientError as e:
            print e
            return


        log_print("### New Instances: ###", verbose)

        for vm in new_instances:
            self.log_print(vm.id + " " +  vm.public_dns_name, verbose)

        return new_instances

    def log_print(self,msg, verbose):
        if verbose:
            print msg


    #google functions
    
    def wait_for_operation(self, compute, project, zone, operation): 
        print('Waiting for operation to finish...')
        while True:
            result = compute.zoneOperations().get(
            project=project,
            zone=zone,
            operation=operation).execute()

            if result['status'] == 'DONE':
                print("done.")
                if 'error' in result:
                    raise Exception(result['error'])
                return result

            time.sleep(1)
    
    def create_instance(self, compute, project, zone, name, bucket, vcpu_number, mem_number):
        # Get the latest Debian Jessie image.
        image_response = compute.images().getFromFamily(
        project='ubuntu-os-cloud', family='ubuntu-1804-lts').execute()
        source_disk_image = image_response['selfLink']

        # Configure the machine
        machine_type = "zones/%s/machineTypes/custom-%s-%s" % (zone, str(vcpu_number), str(mem_number*1024))
        startup_script = open(
        os.path.join(
            os.path.dirname(__file__), 'startup-script.sh'), 'r').read()
        image_url = "http://storage.googleapis.com/gce-demo-input/photo.jpg"
        image_caption = "Ready for dessert?"

        config = {
            'name': name,
            'machineType': machine_type,

            # Specify the boot disk and the image to use as a source.
            'disks': [
                {
                    'boot': True,
                    'autoDelete': True,
                    'initializeParams': {
                    'sourceImage': source_disk_image,
                    }
                }
            ],

            # Specify a network interface with NAT to access the public
            # internet.
            'networkInterfaces': [{
                'network': 'global/networks/default',
                'accessConfigs': [
                    {'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}
                ]
            }],

            # Allow the instance to access cloud storage and logging.
            'serviceAccounts': [{
                'email': 'default',
                'scopes': [
                    'https://www.googleapis.com/auth/devstorage.read_write',
                    'https://www.googleapis.com/auth/logging.write'

                ]
            }],

            # Metadata is readable from the instance and allows you to
            # pass configuration from deployment scripts to instances.
            'metadata': {
                'items': [{
                    # Startup script is automatically executed by the
                    # instance upon startup.
                    'key': 'startup-script',
                    'value': startup_script
                }, {
                    'key': 'url',
                    'value': image_url
                }, {
                    'key': 'text',
                    'value': image_caption
                }, {
                    'key': 'bucket',
                    'value': bucket
                }]
            }
        }
        return compute.instances().insert(
            project=project,
            zone=zone,
            body=config).execute()
    #'https://www.googleapis.com/compute/v1/projects/scheduling/zones/%s/instances/%s/start'
    #'https://www.googleapis.com/compute/v1/projects/myproject/zones/%s/instances/%s/reset'
    
    def delete_instance(self, compute, project, zone, name):
        return compute.instances().delete(
            project=project,
            zone=zone,
            instance=name).execute()
        
    def list_instances(self, compute, project, zone):
        result = compute.instances().list(project=project, zone=zone).execute()
        return result['items']        
            
    def startInstance(auth_http, compute, project, zone, instance):
        return compute.instances().start(project, zone, instance).execute()
    
    def stopInstance(auth_http, compute, project, zone, instance):
        return compute.instances().stop(project, zone, instance).execute()
            
            
            
