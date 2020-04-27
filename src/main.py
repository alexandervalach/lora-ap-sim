#!/usr/bin/python

import getopt
import sys
import time
import random

from access_point import AccessPoint
from connection_controller import ConnectionController
from end_node import EndNode
from bandit_node import BanditNode
from generator import load_nodes


def main(argv):
    ap_id = ''
    register_nodes = False
    shuffle_nodes = False
    duty_cycle_na = 0
    node_file = "data/group1.txt"
    bandit_nodes = 0

    # Reading arguments from command line
    try:
        opts, args = getopt.getopt(argv, "hi:rsf:ab", ["id=", "file=", "help", "register", "shuffle", "bandit"])
    except getopt.GetoptError:
        print("main.py -i <access-point-id> [-r -s]")
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print("main.py -i <access-point-id>\n")
            print("-i <dev_id>, --id=<dev_id>\t- Specify LoRa AP hardware id")
            print("-r, --register\t\t- Include end nodes registration process")
            print("-s, --shuffle\t\t- Shuffle list of end nodes")
            print("-f <file_path>, --file=<file_path>\t- Specify LoRa node id file")
            sys.exit(0)
        elif opt in ("-i", "--id"):
            ap_id = arg
        elif opt in ("-r", "--regen"):
            register_nodes = True
        elif opt in ("-s", "--shuffle"):
            shuffle_nodes = True
        elif opt in ("-f", "--file"):
            node_file = arg
        elif opt in ("-b", "--bandit"):
            bandit_nodes = 1

    # If there was an AP id defined
    if ap_id:
        access_point = AccessPoint(ap_id)
        conn = ConnectionController('147.175.149.229', 25001)
        conn.connect()

        setr_message = access_point.generate_setr()

        if setr_message is not None:
            print(str(setr_message, 'ascii'))
            access_point.process_reply(conn.send_data(setr_message))

        node_ids = load_nodes(node_file)

        if shuffle_nodes:
            random.shuffle(node_ids)

        nodes = []

        for node_id in node_ids:
            if bandit_nodes == 1:
                nodes.append(BanditNode(node_id))
            else:
                nodes.append(EndNode(node_id))

        if register_nodes:
            for node in nodes:
                regr_message = node.generate_message('reg')

                if regr_message is None:
                    print("WARNING: Message from node " + node.get_dev_id() + " could not be sent")
                else:
                    print(str(regr_message, 'ascii'))
                    reply = conn.send_data(regr_message)

                    # Access point duty cycle refresh
                    if duty_cycle_na != 1:
                        airtime = node.process_reply(reply)
                    else:
                        airtime = 0

                    if airtime is not None:
                        duty_cycle_na = access_point.set_remaining_duty_cycle(airtime)

                # time.sleep(1)

        while True:
            for node in nodes:
                rxl_message = node.generate_message('normal')

                if rxl_message is None:
                    print("WARNING: Message from node " + node.get_dev_id() + " could not be sent")
                else:
                    print(str(rxl_message, 'ascii'))
                    reply = conn.send_data(rxl_message)

                    # Access point duty cycle refresh
                    if duty_cycle_na != 1:
                        airtime = node.process_reply(reply)
                    else:
                        airtime = 0

                    if airtime is not None:
                        duty_cycle_na = access_point.set_remaining_duty_cycle(airtime)

            # time.sleep(1)


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        print("Python script finished!")
