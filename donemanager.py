#!/usr/bin/env python
import time
import sys


def log(message, at):
    print time.asctime(at), message


if __name__ == '__main__':
    if len(sys.argv) < 1:
        print "Please enter a message."
    else:
        log(sys.argv[1], time.localtime())
