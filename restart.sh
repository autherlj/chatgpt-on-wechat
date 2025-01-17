#!/bin/bash

# Find the process ID of the running Python3 app.py
process_id=$(ps -ef | grep "python3 app.py" | grep -v "grep" | awk '{print $2}')

# If the process is found, gracefully stop it using the process ID
if [ ! -z "$process_id" ]; then
    echo "Stopping app.py with process ID: $process_id"
    kill -15 "$process_id"
    while kill -0 "$process_id" 2> /dev/null; do
        sleep 1
    done
else
    echo "No app.py process found."
fi

# Restart the app.py and monitor the nohup.out log
echo "Starting app.py..."
nohup python3 app.py & tail -f nohup.out &

