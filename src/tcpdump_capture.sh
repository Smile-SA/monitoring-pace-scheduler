#!/bin/bash

# Check if the required parameters are passed
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <output_file> <duration_in_minutes>"
    exit 1
fi

# Parameters passed to the script
OUTPUT_FILE=$1
DURATION=$((60 * $2))  # Convert minutes to seconds

# Interface and port
INTERFACE="lo"
PORT="9090"

# Run tcpdump with timeout
sudo timeout $DURATION tcpdump -i $INTERFACE port $PORT -w $OUTPUT_FILE

