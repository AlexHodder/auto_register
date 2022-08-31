## Python file to call uiautomator wrapper to dump

from uiautomator import device as d
d.dump('dump.xml', True, True)
