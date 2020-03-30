#!/usr/bin/python

from connection_controller import ConnectionController
from end_node import EndNode
from access_point import AccessPoint
import time, sys, getopt


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
        setr_message = access_point.generate_setr()
        print(setr_message)
        host = '147.175.149.229'
        port = 25001

        conn = ConnectionController(host, port)
        conn.connect()
        conn.send_data(setr_message)
        end_node = EndNode()

        node_ids = ['yv4j', 'ALBY', 'QUFB', 'ALEX', 'Jaro', 'D4n0', 'J4r0']
        seq = 1

        for node_id in node_ids:
            conn.send_data(end_node.generate_regr(node_id))

        while True:
            for node_id in node_ids:
                conn.send_data(end_node.generate_rxl(node_id, seq))
            seq += 1
            time.sleep(5)


if __name__ == "__main__":
    main(sys.argv[1:])
