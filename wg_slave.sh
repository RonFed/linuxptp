#!/bin/bash

# Command 1
./linuxptp/wireguard/setup_wg2.sh

# Command 2
./linuxptp/linuxptp/ptp4l -i eth0 -S -m -f linuxptp/configs/wg_B.cfg  > /linuxptp/plotting/wg_auth_demo_output.txt