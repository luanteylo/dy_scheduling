#! /usr/bin/python

class printer:

    def __init__(self, verbose=False):
        self.verbose =  verbose

    def puts(self, content, warning=False):

        if self.verbose or warning:
            print content

    def write_file(self, path, name, content, mode="w"):
    	with open(path + name, mode) as file:
    		file.write(content);