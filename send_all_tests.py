
#! /usr/bin/python

import argparse
import subprocess



def main():
    
    
    ps = []
    for x in range(0, 5):
            p = subprocess.Popen("python dy_scheduling.py --module aws --config amazon1.conf", shell=True)
            ps.append(p)
            p = subprocess.Popen("python dy_scheduling.py --module aws --config amazon2.conf", shell=True)
            ps.append(p)
            p = subprocess.Popen("python dy_scheduling.py --module aws --config amazon3.conf", shell=True)
            ps.append(p)

    for p in ps:
            p.wait()
    ps = []
    for x in range(0, 5):
            p = subprocess.Popen("python dy_scheduling.py --module aws --config amazon4.conf", shell=True)
            ps.append(p)
            p = subprocess.Popen("python dy_scheduling.py --module aws --config amazon5.conf", shell=True)
            ps.append(p)
            p = subprocess.Popen("python dy_scheduling.py --module aws --config amazon6conf", shell=True)
            ps.append(p)

    for p in ps:
            p.wait()

		

	
if __name__ == "__main__":
	main()
