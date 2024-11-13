#!/bin/bash

# Get the directory of the script
SCRIPT_DIR=$(dirname "$0")
cd "$SCRIPT_DIR/../spa"
npm run dev </dev/null >>./npm.log 2>&1
