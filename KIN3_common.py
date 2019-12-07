import time

def timestamp_short():
	time_now = time.time()
	timestamp = time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(time_now))

	return timestamp

def timestamp():
	time_now = time.time()
	timestamp = time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(time_now))

	decimal = str(round(time_now % 1, 4))[2:]
	padding = '0' * max((0, 4 - len(decimal)))
	timestamp += f'.{decimal}{padding}'

	return timestamp
