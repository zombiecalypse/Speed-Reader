
#!/usr/bin/env python
import SpeedRead
import argparse
from SpeedRead import *

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description = "Helps you train speed reading")
	parser.add_argument('-V', '--version', action='version', version = '%(prog)s {}'.format(version))
	args = parser.parse_args()
	app = SpeedRead()
	app.MainLoop()
	app.OnExit()
