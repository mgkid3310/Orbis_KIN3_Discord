import time

def timestamp():
	return time.strftime('%c', time.localtime(time.time()))
