#!/bin/bash

# Command 1
./run_demo_no_auth.sh

# Command 2
./run_demo_tlv.sh

# Command 3
./run_demo_wg.sh

# Command 4
sleep 20

# Command 5
winpty python ./plotting/plotter_demo.py