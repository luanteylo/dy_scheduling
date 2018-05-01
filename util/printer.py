#! /usr/bin/python

class printer:

    def __init__(self, verbose=False):
        self.verbose =  verbose

    def puts(self, content, warning=False):

        if self.verbose or warning:
            print content