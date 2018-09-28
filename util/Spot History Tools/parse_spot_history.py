from datetime import datetime

path = "/home/luan/Dropbox/UFF - Doutorado/traces/spot_history/"
path_output = "/home/luan/Dropbox/UFF - Doutorado/traces/spot_history/by_type/"

name_input = "us-west-1.csv"
name_output = "us-west-1-%s.csv"

types = [
    "c3.4xlarge",
    "r3.2xlarge",
    "c4.8xlarge",
    "c3.8xlarge",
    "m2.xlarge",
    "g2.2xlarge",
    "m4.16xlarge",
    "c3.xlarge",
    "m4.2xlarge",
    "d2.2xlarge",
    "m4.4xlarge",
    "r3.4xlarge",
    "r4.2xlarge",
    "r4.4xlarge",
    "i3.xlarge",
    "c4.4xlarge",
    "m3.2xlarge",
    "r4.16xlarge",
    "c4.xlarge",
    "r3.xlarge",
    "m4.10xlarge",
    "m3.xlarge",
    "m4.xlarge",
    "c4.2xlarge",
    "r3.large",
    "m3.large",
    "c3.2xlarge",
    "r3.8xlarge",
    "d2.xlarge",
    "m2.4xlarge",
    "i2.xlarge",
    "d2.8xlarge",
    "i2.8xlarge",
    "m1.medium",
    "c1.xlarge",
    "c1.medium",
    "r4.xlarge",
    "i2.2xlarge",
    "c4.large",
    "m2.2xlarge",
    "i3.16xlarge",
    "i3.4xlarge",
    "i2.4xlarge",
    "i3.2xlarge",
    "g2.8xlarge",
    "i3.8xlarge",
    "m3.medium",
    "m4.large",
    "r4.8xlarge",
    "i3.large",
    "r4.large",
    "d2.4xlarge",
    "m1.xlarge",
    "c3.large",
    "m1.large",
    "m1.small",
    "t1.micro",
]

FMT = '%Y-%m-%d %H:%M:%S'

for type in types:

    output = "timestamp, seconds, instance, price\n"
    s1 = ""
    s2 = ""

    with open(path + name_input) as f:

        for line in reversed(f.readlines()):
            if line.split(",")[2] == "Linux/UNIX" and line.split(",")[1] == type and line.split(",")[3] == "us-west-1c":
                time_stemp = line.split(',')[0]
                vm_type = line.split(',')[1]
                price = line.split(',')[4]

                data = time_stemp.split("+")[0]

                second = 0

                if s1 == "":
                    s1 = data
                else:
                    s2 = data

                    tdelta = datetime.strptime(s2, FMT) - datetime.strptime(s1, FMT)

                    second = tdelta.total_seconds()

                output += data + "," + str(second) + "," + vm_type + "," + price

    with open(path_output + name_output % (type,), "w") as f:
        f.write(output)
        print name_output % (type,), "\t...ok"
