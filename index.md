## LoRa AP Simulator

STIoT packet generator which simulates LoRa@FIIT wireless access point and LoRa@FIIT end nodes.

## API Documentation
API documentation generated with doxygen is available [online](https://alexandervalach.github.io/lora-ap-sim/docs/annotated.html).

## Supported features and TODO
### Access Points features

#### LoRa Concentrator Features Support
- [X] Pseudo-random RSSI, SNR generation
- [X] Sending frequency data in STIoT messages
- [X] Command line interface
- [X] Duty cycle contraints and refresh

#### Thread-safe Features
- [X] Non-blocking socket communication to improve scalability
- [X] Thread-safe message queuing

#### QoS Support
- [X] Emergency message support
- [X] Priority queue for emergency messages

#### Collisions
- [X] Uplink collision simulation
- [X] Downlink collision simulation

### End Nodes Features
- [X] End node duty cycle constraints and refresh
- [X] Processing network data from network server to adapt communication parameters
- [X] Calculate time-on-air (TOA) for each message
- [X] Data retransmission in case of collision
- [X] Support for MABP statistical model and channel selection
- [X] Support for Upper Confidence Bound parameter selection
- [ ] Support for Thompson Sampling parameter selection

## Command line interface

### End nodes generation is required if data folder is empty
You are free to change these variables in generator.py:
```
file_path="data/group1.txt"
num_of_nodes = 100
```

Then you should run
```
generator.py
```

### Single access point usage
Recommended approach.
Could be displayed by running main.py -h or main.py --help commands
```
main.py -i <access-point-id>

-i <dev_id>, --id=<dev_id> - Specify LoRa AP hardware id

-r, --register - Include end nodes registration process

-s, --shuffle - Shuffle list of end nodes

-f <file_path>, --file=<file_path> - Specify LoRa node id file

-b, --bandit - Activating bandit nodes support

-t, --test - Using test scenario for developing purposes
```

### Multi access point usage
Just run the file. It generates 10x[number of files] new access points.
This usage is buggy and can cause memmory leaks.
Use at your own risk.
```
run.py
```
