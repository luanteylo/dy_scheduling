from botocore.exceptions import ClientError

import timeit

import boto3


def get_instances(ec2_client, filters=[], InstanceIds=[]):
    """
    :type ec2_client: pyboto3.ec2
    :return: pyboto3.Ec2.Instance
    """

    try:
        response = ec2_client.describe_instances(Filters=filters, InstanceIds=InstanceIds)
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


def stop_instances(ec2_client, instance_ids=[], verbose=False):
    """
    :type ec2_client: pyboto3.ec2
    :type instance_ids: list[str]
    :return:
    """

    filter = [
        {'Name': 'instance-state-name',
         'Values': ['running']}
        ]

    running_instances = get_instances(ec2_client, filters=filter, InstanceIds=instance_ids)

    if not running_instances:
        return

    for vm in running_instances:
        log_print("Stopping: " + vm.id, verbose)
        vm.stop()


def start_instances(ec2_client, instance_ids=[], verbose=False):
    """
    :type ec2_client: pyboto3.ec2
    :type instance_ids: list[str]
    :return:
    """

    filter = [
        {'Name': 'instance-state-name',
         'Values': ['stopped']}
        ]

    running_instances = get_instances(ec2_client, filters=filter, InstanceIds=instance_ids)

    if not running_instances:
        return

    try:
        for vm in running_instances:
            log_print("Starting: " + vm.id, verbose)
            vm.start()
    except ClientError as e:
        print e
        return 


def terminate_instances(ec2_client, InstanceIds = [], verbose=False):
    '''
    :type ec2_client: pyboto3.ec2
    :return:
    '''

    filter = [
        {'Name': 'instance-state-name',
         'Values': ['running', 'stopped']}
    ]

    instances = get_instances(ec2_client, filters=filter, InstanceIds=InstanceIds)

    if not instances:
        return
    instances_ids = []
    for vm in instances:
        log_print("Terminating: " + vm.id, verbose)
        vm.terminate()
        instances_ids.append(vm.id)

    waiter = ec2_client.get_waiter('instance_terminated')
    waiter.wait(InstanceIds=instances_ids)



def create_instances(imageId, instanceType, securityGroups=['launch-wizard-2'],keyName='ec2', minCount=1, maxCount=1, verbose=False):
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
        log_print(vm.id + " " +  vm.public_dns_name, verbose)

    return new_instances


def print_all_instances(ec2_client):
    instances = get_instances(ec2_client)

    if not instances:
        return

    for vm in instances:
        print vm.id + " " +  vm.instance_type + " " +  vm.state['Name']


def log_print(msg, verbose):
    if verbose:
        print msg

