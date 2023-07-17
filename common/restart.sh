#!/bin/bash

# Find the process ID of the running Python3 sync_openid_job.py
process_id=$(ps -ef | grep "python3 sync_openid_job.py" | grep -v "grep" | awk '{print $2}')

# If the process is found, gracefully stop it using the process ID
if [ ! -z "$process_id" ]; then
    echo "Stopping sync_openid_job.py with process ID: $process_id"
    kill -15 "$process_id"
    sleep 2
else
    echo "No sync_openid_job.py process found."
fi

# Restart the sync_openid_job.py and monitor the nohup.out log
echo "Starting sync_openid_job.py..."
nohup python3 sync_openid_job.py & tail -f nohup.out &

