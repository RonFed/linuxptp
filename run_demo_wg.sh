#!/bin/bash

# Array to store background process IDs
pids=()

# windows format path of pwd
dockerfile_path=$(pwd -W | sed 's,/,\\,g')

# Function to create Docker image and run code
create_image_and_run_code() {
    local image_name="ptp_image"
    local image_setup_name=$1
    local code_to_run=$2

    echo "Creating Docker image: $image_setup_name"
    winpty docker run --rm -it --network=demo3 --name $image_setup_name --cap-add=NET_ADMIN -v "$dockerfile_path":/linuxptp "$image_name" //usr/bin/bash -c "$code_to_run"
}

# Images codes
code1_to_run="./linuxptp/master_wg.sh"
code2_to_run="./linuxptp/slave_wg.sh"
code4_to_run="./linuxptp/eve.sh"

# Function to kill all background processes
kill_background_processes() {
    echo "Killing all background processes..."
    for pid in "${pids[@]}"; do
        kill "$pid"
    done
    docker kill $(docker ps -q)
}

# Trap signal handler to kill background processes
trap 'kill_background_processes' SIGINT SIGTERM

# Create and run code in each image
create_image_and_run_code "Master-WireGuard" "$code1_to_run" &
pids+=($!)
sleep 2
create_image_and_run_code "Slave-WireGuard" "$code2_to_run" & 
pids+=($!)
#sleep 15
#winpty python ./plotting/plotter_demo.py &
#pids+=($!)
create_image_and_run_code "Eve-WireGuard" "$code4_to_run" 
pids+=($!)

# Wait for all background processes to finish
wait

# Wait for user input before exiting
echo "Press CTRL+C to exit..."
while true; do
  sleep 1
done
