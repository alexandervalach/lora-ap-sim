from connection_controller import ConnectionController
import time

setrMessage = '{"message_name": "SETR","message_body": {"id": "11111111","ver": 1.0,"m_chan": true,"channels": 8,"sup_freqs": [863000000,100000,870000000],"sup_sfs": [7,8,9,10,11,12],"sup_crs": ["4/5","4/6","4/7","4/8"],"sup_bands": [500000,250000,125000],"lora_stand": {"name": "Lora@FIIT","version": "1.0"},"max_power": 14}}'
regrMessage = '{"message_name":"REGR", "message_body":{ "band": 125000, "cr": "4/5", "dev_id":"ALBY", "power":14, "duty_c": 36000, "rssi": -57.0, "sf": 9, "snr": 10.75, "time": 15752, "app_data":"TE9SQUZJSVQ=", "sh_key":"+/////v////7////+////wIAAAA=" }}'
host = '147.175.149.229'
port = 25001

conn = ConnectionController(host, port)
conn.connect()
conn.send_data(setrMessage)
# conn.send_data(regrMessage)

while True:
    conn.send_data(regrMessage)
    time.sleep(10)