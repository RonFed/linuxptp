#!/bin/bash

# Command 1
./linuxptp/wireguard/setup_wg3.sh

# Command 2
./linuxptp/linuxptp/ptp4l -i eth0 -S -m -f linuxptp/configs/wg_C.cfg   > /linuxptp/plotting/no_auth_demo_output.txt