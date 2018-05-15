#! /bin/bash
apt update 

apt install -y  gfortran
apt install -y  gcc
apt install -y nfs-common

#`HPC
apt install -y sudo apt install mpi-default-dev
apt install -y mpich
apt install -y libatlas-base-dev
apt install -y libblas-dev liblapack-dev


#Setup NFS
mkdir /nfs/general -p
mount 10.100.10.86:/var/nfs/general /nfs/general


cp  /nfs/general/config/guests/NPB3.3-OMP.tar.gz   .
tar -xf NPB3.3-OMP.tar.gz


#update /etc/fstab
echo "10.100.10.86:/var/nfs/general /nfs/general nfs auto,nofail,noatime,nolock,intr,tcp,actimeo=1800 0 0" >> /etc/fstab

#enable console 
systemctl enable serial-getty@ttyS0.service
systemctl start serial-getty@ttyS0.service


#test 


# Clean instalation
rm NPB3.3-OMP.tar.gz
