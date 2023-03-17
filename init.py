import daemon
import os
import logging

def main():
	try:
		with daemon.DaemonContext():
			logging.basicConfig(filename='/home/abishekdevendran/jasonDaemon.log', level=logging.DEBUG)
			logging.debug('Starting daemon...')
			print("check")
			os.execv('/bin/python3', ['python3', '/mnt/sda1/GitHub/Jason/main.py'])
	except:
		print("Something's wrong I can feel it.")

if __name__ == '__main__':
	main()
