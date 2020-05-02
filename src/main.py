#!/usr/bin/python

import getopt
import sys
import random
import time
import json

from multiprocessing import Process, Queue
from access_point import AccessPoint
from connection_controller import ConnectionController
from end_node import EndNode
# from bandit_node import BanditNode
from generator import load_nodes

sock = None
conn = None


def read_reply(queue, access_point, nodes):
    message = queue.get(timeout=1)
    reply = conn.send_data(message.json_message)

    if reply is not None:
        # First '{' is doubled for unknown reason, let's remove it
        reply = reply[1:]
        reply_dict = json.loads(reply)

        dev_id = reply_dict['message_body']['dev_id']

        if access_point.duty_cycle_na != 1:
            toa = nodes[dev_id].process_reply(reply_dict)
        else:
            print("Could not send any downlink messages till next duty cycle refresh")
            toa = 0

        if toa is not None:
            access_point.set_remaining_duty_cycle(toa)


def main(argv):
    ap_id = '111111'
    register_nodes = False
    shuffle_nodes = False
    duty_cycle_na = 0
    node_file = "data/group10.txt"
    bandit_nodes = False
    test_scenario = False

    # Reading arguments from command line
    try:
        opts, args = getopt.getopt(argv, "hi:rsf:abt", ["id=", "file=", "help", "register", "shuffle", "bandit", "test"])
    except getopt.GetoptError:
        print("main.py -i <access-point-id> [-r -s -t]")
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
            bandit_nodes = True
        elif opt in ("-t", "--test"):
            test_scenario = True

    # If there was an AP id defined
    conn.connect('147.175.149.229', 25001)
    access_point = AccessPoint(ap_id, conn)
    access_point.send_setr()

    if test_scenario:
        node_ids = ['KmoT', 'meQy', 'meBh', 'cbun', 'ttYa']
    else:
        node_ids = load_nodes(node_file)

    if shuffle_nodes:
        random.shuffle(node_ids)

    nodes = {}
    processes = {}

    message_queue = Queue()
    emergency_queue = Queue()
    num_of_nodes = 0

    while True:
        while not message_queue.empty() or not emergency_queue.empty():
            try:
                while not emergency_queue.empty():
                    read_reply(emergency_queue, access_point, nodes)

                read_reply(message_queue, access_point, nodes)
            except Exception as qe:
                print(qe)

        if num_of_nodes < len(node_ids):
            node_id = node_ids[num_of_nodes]
            """
            if bandit_nodes:
                nodes[node_id] = BanditNode(node_id)
            else:
            """
            node = EndNode(node_id, register_nodes)
            process = Process(target=node.device_routine, args=(message_queue, emergency_queue,))
            process.daemon = True
            process.start()
            processes[node_id] = process
            nodes[node_id] = node

            num_of_nodes += 1
            time.sleep(random.randrange(30))
        else:
            time.sleep(random.randrange(3))


if __name__ == "__main__":
    try:
        conn = ConnectionController()
        main(sys.argv[1:])
    except KeyboardInterrupt:
        print("")

        if conn is not None:
            conn.close()
            print("Connection closed")

        print("Python script finished")
