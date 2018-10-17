#! /bin/bash


#NETWORK VARs
PORT="enp2s0"
IP="10.100.10.86"


sudo add-apt-repository ppa:jacob/virtualisation
sudo apt update


#qemu/kvm
sudo apt install -y qemu
sudo apt install -y libvirt-bin
sudo apt install -y qemu-kvm
sudo apt install -y virtinst

#iscsi-client
sudo apt install -y open-iscsi parted

#glusterfs
sudo apt install -y glusterfs-server
sudo apt install -y glusterfs-client
sudo apt install -y attr


#General Softwares
sudo apt install -y vim
sudo apt install -y vnc-java
sudo apt install -y default-jr
sudo apt install -y screen


#SSH
sudo apt install -y openssh-server
sudo apt install -y openssh-client

#NFS
sudo apt-get install nfs-common

#python
sudo apt install python-pip python-dev pkg-config build-essential autoconf libvirt-dev
# sudo pip install libvirt-python
# sudo pip install configparser

printf "Installation...\t Done\n"


cat hosts.conf >> /etc/hosts
printf "Setup /etc/hosts...\t Done\n"

cat interfaces.conf | sed  "s/PORT/$PORT/" | sed "s/XXXX/$IP/" > /etc/network/interfaces

printf "Check the interfaces file\n"
printf "Setup /etc/network/interfaces \t...(ok)\n"

#update /etc/fstab
cat fstab.conf >> /etc/fstab
printf "Setup /etc/fstab...\t Done\n"


# cp  qemu.conf /etc/libvirt/
# sudo /etc/init.d/libvirt-bin restart
# printf "Setup /etc/libvirt/qemu.conf...\t Done\n"s

cp iscsi-client/*  /etc/iscsi/
printf "Setup /etc/iscsi/...\t Done\n"






