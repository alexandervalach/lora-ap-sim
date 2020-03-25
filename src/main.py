from connection_controller import ConnectionController
from end_node import EndNode
import time

setr_message = '{"message_name": "SETR","message_body": {"id": "11111111","ver": 1.0,"m_chan": true,"channels": 8,"sup_freqs": [863000000,100000,870000000],"sup_sfs": [7,8,9,10,11,12],"sup_crs": ["4/5","4/6","4/7","4/8"],"sup_bands": [500000,250000,125000],"lora_stand": {"name": "Lora@FIIT","version": "1.0"},"max_power": 14}}'
host = '147.175.149.229'
port = 25001

conn = ConnectionController(host, port)
conn.connect()
conn.send_data(setr_message)
end_node = EndNode()

node_ids = ['yv4j', 'ALBY', 'QUFB', 'ALEX', 'Jaro']
seq = 1

while True:
    for node_id in node_ids:
        rxl_message = end_node.generate_rxl(node_id, seq)
        conn.send_data(rxl_message)
    seq += 1
    time.sleep(10)