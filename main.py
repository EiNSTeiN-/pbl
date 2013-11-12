#!/usr/bin/python

import sys
import os

path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(path)

from pbl import poll

if __name__ == "__main__":
    poll.main()
