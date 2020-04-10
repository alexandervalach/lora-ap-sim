#!/usr/bin/python

import getopt
import sys
import time

from access_point import AccessPoint
from connection_controller import ConnectionController
from end_node import EndNode
from generator import load_nodes


def main(argv):
    ap_id = ''
    register_nodes = False

    """ Reading arguments from command line """
    try:
        opts, args = getopt.getopt(argv, "hi:r", ["id="])
    except getopt.GetoptError:
        print("main.py -i <access-point-id>")
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print("main.py -i <access-point-id>")
            sys.exit(0)
        elif opt in ("-i", "--id"):
            ap_id = arg
        elif opt in ("-r", "--register"):
            register_nodes = True

    """ If there was an AP id defined """
    if ap_id:
        access_point = AccessPoint(ap_id)
        conn = ConnectionController('147.175.149.229', 25001)
        conn.connect()
        setr_message = access_point.generate_setr()
        print(setr_message)
        access_point.process_reply(conn.send_data(setr_message))

        node_ids = load_nodes("data/group1.txt")
        nodes = []

        for node_id in node_ids:
            nodes.append(EndNode(node_id))

        if register_nodes:
            for node in nodes:
                regr_message = node.generate_regr()
                print(regr_message)
                node.process_reply(conn.send_data(regr_message))
                time.sleep(1)

        while True:
            for node in nodes:
                rxl_message = node.generate_rxl()
                print(rxl_message)

                if rxl_message is None:
                    print("WARNING: Message from node " + node.get_dev_id() + " could not be sent")
                else:
                    node.process_reply(conn.send_data(rxl_message))

            time.sleep(1)


if __name__ == "__main__":
    main(sys.argv[1:])
