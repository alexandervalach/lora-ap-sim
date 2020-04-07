#!/usr/bin/python

import getopt
import sys
import time

from access_point import AccessPoint
from connection_controller import ConnectionController
from end_node import EndNode


def main(argv):
    ap_id = ''

    try:
        opts, args = getopt.getopt(argv, "hi:", ["id="])
    except getopt.GetoptError:
        print("main.py -i <access-point-id>")
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print("main.py -i <access-point-id>")
            sys.exit(0)
        elif opt in ("-i", "--id"):
            ap_id = arg

    if ap_id:
        access_point = AccessPoint(ap_id)
        conn = ConnectionController('147.175.149.229', 25001)
        conn.connect()
        conn.send_data(access_point.generate_setr())

        node_ids = ['yv4j', 'ALBY', 'QUFB', 'ALEX', 'Jaro', 'D4n0', 'J4r0']
        nodes = []

        for node_id in node_ids:
            nodes.append(EndNode(node_id))

        for node in nodes:
            conn.send_data(node.generate_regr())

        while True:
            for node in nodes:
                message = node.generate_rxl()

                if message is None:
                    print("WARNING: Message from node " + node.get_dev_id() + " could not be sent")
                else:
                    conn.send_data(message)

            time.sleep(5)


if __name__ == "__main__":
    main(sys.argv[1:])
