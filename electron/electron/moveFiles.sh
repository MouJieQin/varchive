#!/bin/bash

echo "Moving files to resource..."
# Get the directory of the script
SCRIPT_DIR=$(dirname "$0")
VARCHIVE_DIR=$(
    cd "$SCRIPT_DIR/../../.."
    pwd
)
RESOURCE_DIR="$VARCHIVE_DIR/electron/Varchive/dist_electron/mac/Varchive.app/Contents/Resources"
if [ ! -d "$RESOURCE_DIR" ]; then
    echo "Not exist: $RESOURCE_DIR" 1>&2
    exit 1
fi
cd "$VARCHIVE_DIR"
for file in $(git ls-files); do
    dir=$(dirname "$file")
    theResourceDir="$RESOURCE_DIR/$dir"
    if [ ! -d "$theResourceDir" ]; then
        mkdir -p "$theResourceDir"
    fi
    cp "$file" "$theResourceDir"
done
cd -

cd "$RESOURCE_DIR/spa/"
npm install
cd -
