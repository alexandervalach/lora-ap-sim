# LoRa@FIIT Access Point and End Nodes simulator
STIoT packet generator which simulates LoRa@FIIT wireless access point and LoRa@FIIT end nodes.

## Supported features and TODO
### Access Points features
- [X] Pseudo-random RSSI, SNR generation
- [X] Sending frequency data to further improve channel utilization
- [X] Emergency message support
- [X] Command line interface
- [X] Differentiate between static and mobile node parameter selection
- [X] Access Point duty cycle contraints and refresh
- [X] Multiaccess point command line usage
- [X] Fake non-blocking socket communication to improve scalability
- [ ] Non-blocking socket communication to improve scalability
- [ ] Collision simulation

### End nodes features
- [X] End node duty cycle constraints and refresh
- [X] Processing network data from network server to adapt communication parameters
- [X] Calculate time-on-air (TOA) for each message
- [ ] Data retransmission in case of collision
- [ ] Support for MABP statistical model and channel selection

## Command line interface

### End nodes generation is required if data folder is empty
You should run
```
generator.py
```

### Single access point usage
Could be displayed by running main.py -h or main.py --help commands
```
main.py -i <access-point-id>

-i <dev_id>, --id=<dev_id> - Specify LoRa AP hardware id

-r, --register - Include end nodes registration process

-s, --shuffle - Shuffle list of end nodes

-f <file_path>, --file=<file_path> - Specify LoRa node id file
```

### Multi access point usage
Just run the file. It generates 10x[number of files] new access points.
This server as lightweight "non-blocking socket communication"
```
run.py
```
