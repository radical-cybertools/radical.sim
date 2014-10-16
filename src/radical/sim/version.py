__copyright__ = "Copyright 2014, http://radical.rutgers.edu"
__license__   = "MIT"

import os

dirname = os.path.dirname(os.path.abspath(__file__))

version = open(
    os.path.join(dirname, "VERSION"), 'r').read().strip()
version_detail = open(
    os.path.join(dirname, "VERSION.git"), 'r').read().strip()
