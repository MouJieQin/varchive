#!/bin/bash

ps -ef | grep varchive-server.py | grep -v grep | awk '{print $2}' | xargs -I {} kill -15 {}
ps -ef | grep varchive-client.sh | grep -v grep | awk '{print $2}' | xargs -I {} kill -15 {}
ps -ef | grep node | grep -i varchive | grep -v grep | awk '{print $2}' | xargs -I {} kill -15 {}

TOTAL=5
count=0
while ps -ef | grep varchive-server.py | grep -v grep; do
    let count=count+1
    if [ $count -ge $TOTAL ]; then
        ps -ef | grep varchive-server.py | grep -v grep | awk '{print $2}' | xargs -I {} kill -9 {}
    fi
    sleep 1
done

count=0
while ps -ef | grep varchive-client.sh | grep -v grep; do
    let count=count+1
    if [ $count -ge $TOTAL ]; then
        ps -ef | grep varchive-client.sh | grep -v grep | awk '{print $2}' | xargs -I {} kill -9 {}
    fi
    sleep 1
done

count=0
while ps -ef | grep node | grep -i varchive | grep -v grep; do
    let count=count+1
    if [ $count -ge $TOTAL ]; then
        ps -ef | grep node | grep -i varchive | grep -v grep | awk '{print $2}' | xargs -I {} kill -9 {}
    fi
    sleep 1
done