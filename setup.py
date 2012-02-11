
from setuptools import setup
from SpeedRead import version

setup(
	name = 'SpeedRead',
	version = version,
	description = 'Helps you train speed reading',
	author = "None",
	author_email = "None",
	scripts = ['SpeedRead.py'],
	packages = ['SpeedRead'],
	install_requires = ["setuptools", pikka])
