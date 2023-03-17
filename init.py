import daemon
import os

def main():
    with daemon.DaemonContext():
        os.execv('/bin/python3', ['python3', '/mnt/sda1/GitHub/Jason/main.py'])

if __name__ == '__main__':
    main()
