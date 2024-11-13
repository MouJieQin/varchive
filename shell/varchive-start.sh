#!/bin/bash

if ps -ef | grep varchive-server.py | grep -v grep; then
    echo "Varchive is running!"
    exit 0
fi

# Get the directory of the script
SCRIPT_DIR=$(dirname "$0")
cd "$SCRIPT_DIR"
nohup ./varchive-client.sh >>./varchive-client.log 2>&1 &
cat "$SCRIPT_DIR/../spa/npm.log" | tail -n 7
cd - >/dev/null
cd "$SCRIPT_DIR/../server/src"
nohup python3.9 varchive-server.py >>./server.log 2>&1 &
cd - >/dev/null
