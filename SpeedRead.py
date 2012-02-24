
#!/usr/bin/env python
import SpeedRead
import argparse
import logging
from SpeedRead import *

if __name__ == '__main__':
    #logging.getLogger('Text Actors').setLevel(logging.DEBUG)
    #logging.basicConfig()
    parser = argparse.ArgumentParser(description = "Helps you train speed reading")
    parser.add_argument('-V', '--version', action='version', version = '%(prog)s {}'.format(version))
    args = parser.parse_args()
    app = SpeedRead()
    app.MainLoop()
    app.OnExit()
