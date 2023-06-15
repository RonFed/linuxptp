#!/bin/bash

# Array to store background process IDs
pids=()

# Function to create Docker image and run code
create_image_and_run_code() {
    local image_name="ron/ptp:v0.1"
    local dockerfile_path="C:\Users\shake\OneDrive\Codes\FinalProject"
    local image_setup_name=$1
    local code_to_run=$2
    local output_file=$3

    echo "Creating Docker image: $image_setup_name"
    winpty docker run --rm -it --network=multicast --cap-add=NET_ADMIN -v "$dockerfile_path":/linuxptp "$image_name" //usr/bin/bash -c "$code_to_run" #> "$output_file"
}

# Image 1
code1_to_run="./linuxptp/master.sh"

# Image 2
code2_to_run="./linuxptp/wg_slave.sh"

# Image 3
code3_to_run="./linuxptp/no_auth_slave.sh"

# Image 4
code4_to_run="./linuxptp/eve.sh"

# Function to kill all background processes
kill_background_processes() {
    echo "Killing all background processes..."
    for pid in "${pids[@]}"; do
        kill "$pid"
    done
}

# Trap signal handler to kill background processes
trap 'kill_background_processes' SIGINT SIGTERM

# Create and run code in each image
create_image_and_run_code "Master" "$code1_to_run" "master_output.txt" &
pids+=($!)
create_image_and_run_code "Slave-WireGuard" "$code2_to_run" "wg_slave_output.txt" &
pids+=($!)
create_image_and_run_code "Slave-NoAuth" "$code3_to_run" "no_auth_slave_output.txt" &
pids+=($!)
create_image_and_run_code "Eve" "$code4_to_run" "eve_output.txt" 
pids+=($!)

# Wait for all background processes to finish
wait

# Wait for user input before exiting
read -n 1 -s -r -p "Press any key to exit..."
