#!/usr/bin/python

import sys
import time
import subprocess
import os
import signal

first_id = 111110
last_id = 111120
first_group = 10
last_group = 16
processes = []
register = 0

print("Loading APs configuration...")


def main(argv):
    # dirname = os.getcwd()
    for group in range(first_group, last_group):
        for ap_id in range(first_id, last_id):
            file = "data/group{0}.txt".format(group)

            if register == 1:
                command = "python main.py -i {0} -r -f {1} &".format(ap_id, file)
            else:
                command = "python main.py -i {0} -s -f {1} &".format(ap_id, file)

            command_list = command.split()
            processes.append(subprocess.Popen(command_list))
            time.sleep(1)


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        # Killing processes on keyboard interrupt
        for process in processes:
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        print("LoRa Access Point simulator closed!")
