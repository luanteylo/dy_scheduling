#! /usr/bin/python

import argparse


# my classes
from util.printer import printer
from util.inputParser import inputParser


from modules.migration import migration
from modules.scaling import scaling


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('--config', help='config file name',
                        default='default.conf')
    parser.add_argument('--module', help='Module name',
                        choices=['migration', 'scaling'], default='migration')

    args = parser.parse_args()
    conf = inputParser(args.config)

    if args.module == "migration":

        print "starting Migration project."
        migration(conf).run()

    elif args.module == "scaling":

        print "starting Scaling project."
        scaling(conf).run()


if __name__ == "__main__":
    main()
