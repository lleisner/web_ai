path = '/home/u045/test/web_ai/task2/week1'

import sys
sys.path.insert(1, path)

import os
os.chdir(path)

from test import app as application