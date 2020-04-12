#!/usr/bin/python

import getopt
import sys
import time
import random

from access_point import AccessPoint
from connection_controller import ConnectionController
from end_node import EndNode
from generator import load_nodes


def main(argv):
    ap_id = ''
    register_nodes = False
    shuffle_nodes = False
    node_file = "data/group1.txt"

    """ Reading arguments from command line """
    try:
        opts, args = getopt.getopt(argv, "hi:rsf:", ["id=", "file="])
    except getopt.GetoptError:
        print("main.py -i <access-point-id> [-r -s]")
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print("main.py -i <access-point-id>\n")
            print("-i <dev_id>, --id=<dev_id>\t- Specify LoRa AP hardware id")
            print("-r, --register\t\t- Include device register process")
            print("-s, --shuffle\t\t- Shuffle list of end nodes")
            print("-f <file_path>, --file=<file_path>\t- Specify LoRa node id file")
            sys.exit(0)
        elif opt in ("-i", "--id"):
            ap_id = arg
        elif opt in ("-r", "--register"):
            register_nodes = True
        elif opt in ("-s", "--shuffle"):
            shuffle_nodes = True
        elif opt in ("-f", "--file"):
            node_file = arg

    """ If there was an AP id defined """
    if ap_id:
        access_point = AccessPoint(ap_id)
        conn = ConnectionController('147.175.149.229', 25001)
        conn.connect()
        setr_message = access_point.generate_setr()
        print(setr_message)
        access_point.process_reply(conn.send_data(setr_message))

        node_ids = load_nodes(node_file)

        if shuffle_nodes:
            random.shuffle(node_ids)

        nodes = []

        for node_id in node_ids:
            nodes.append(EndNode(node_id))

        if register_nodes:
            for node in nodes:
                regr_message = node.generate_message('reg')
                print(regr_message)
                reply = conn.send_data(regr_message)
                node.process_reply(reply)
                time.sleep(1)

        while True:
            for node in nodes:
                rxl_message = node.generate_message('normal')
                print(rxl_message)

                if rxl_message is None:
                    print("WARNING: Message from node " + node.get_dev_id() + " could not be sent")
                else:
                    node.process_reply(conn.send_data(rxl_message))

            time.sleep(1)


if __name__ == "__main__":
    main(sys.argv[1:])
