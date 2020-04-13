# LoRa@FIIT Access Point and End Nodes simulator
STIoT packet generator which simulates LoRa@FIIT wireless access point.

Supported features:

[X] Pseudo-random RSSI, SNR generation 
[X] Processing network data from network server to adapt communication parameters
[X] Sending also frequency to improve channel utilization
[X] Emergency message support
[X] End node duty cycle constraints and refresh
[X] Command line interface

TODO:

[] Non-blocking socket communication to improve scalability
[] Differentiate between static and mobile node parameter selection
[] Access Point duty cycle  contraints and refresh
[] Multiaccess point command line usafe

## Command line interface
main.py -i <access-point-id>

-i <dev_id>, --id=<dev_id> - Specify LoRa AP hardware id
-r, --register - Include end nodes registration process
-s, --shuffle - Shuffle list of end nodes
-f <file_path>, --file=<file_path> - Specify LoRa node id file using relative or absolute file path (default is data/group1.txt)
