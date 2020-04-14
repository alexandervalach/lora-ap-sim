#!/usr/bin/python

import random
import string


dev_ids = []
file_path = "data/group1.txt"


def generate_nodes(number_of_nodes=1000, dev_id_length=4):
    for x in range(number_of_nodes):
        dev_ids.append(''.join(random.choices(string.ascii_letters + string.digits, k=dev_id_length)))


def save_nodes(path=file_path):
    file = open(path, "w")
    for dev_id in dev_ids:
        file.write(dev_id + "\n")
    file.close()


def load_nodes(path=file_path):
    ids = []
    file = open(path, "r")
    for line in file:
        ids.append(line.strip())
    file.close()
    return ids