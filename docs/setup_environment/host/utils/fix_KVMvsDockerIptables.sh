#! /bin/bash

sudo iptables -A FORWARD -i br0 -o br0 -j ACCEPT


## Persistent Solution ##
# Create a file /etc/docker/daemon.json with the following contents:
# {
#    "iptables" : false
# }
 
