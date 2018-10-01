import boto3

import re
import urllib2


def get_spot_price(type, region, zone):
    client = boto3.client('ec2', region_name=region)
    prices = client.describe_spot_price_history(InstanceTypes=[type], MaxResults=1,
                                                ProductDescriptions=['Linux/UNIX (Amazon VPC)'],
                                                AvailabilityZone=zone)
    # print type, region, zone, prices
    if not prices['SpotPriceHistory']:
        return None
    else:
        return float(prices['SpotPriceHistory'][0]["SpotPrice"])


def get_ondemand_price():
    pattern_region1 = re.compile("^([a-z]+)\-([a-z]+)\-([0-9])")
    pattern_region2 = re.compile("^([a-z]+)\-([a-z]+)\-([a-z]+)\-([0-9])")
    pattern_instance = re.compile("^([a-z,0-9]+)\.([a-z,0-9]+)")

    response = urllib2.urlopen('http://a0.awsstatic.com/pricing/1/ec2/linux-od.min.js')
    data = response.read()

    output = {}

    for region in data.split("region:"):
        current_region = ""
        for instanceTypes in region.split("instanceTypes:"):
            for size in instanceTypes.split("size:"):
                # print "##########################"
                # print size.split()[0]
                if size.split()[0] not in ["/*", "*"]:
                    # print size
                    key = size.split()[0].split(",")[0].replace('"', '')

                    if pattern_region1.match(key):
                        current_region = key
                        output[current_region] = []

                    elif pattern_instance.match(key) and current_region is not "":

                        # get all instance informations
                        instance_name = size.split(",")[0].replace('"', '').replace("'", "")
                        vcpu = size.split(",")[1].split(":")[1].replace('"', '')
                        memory = size.split(",")[3].split(":")[1].replace('"', '')
                        price_ondemand = size.split(",")[6].split(":")[-1].replace('"', '').split("}")[0]

                        output[current_region].append((instance_name, vcpu, memory, price_ondemand))

    return output


def get_all_zones(region):
    ec2 = boto3.client('ec2', region_name=region)
    zones = []
    # Retrieves availability zones only for region of the ec2 object
    response = ec2.describe_availability_zones()
    for zone in response["AvailabilityZones"]:
        zones.append(zone["ZoneName"])

    return zones