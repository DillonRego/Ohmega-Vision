#!/bin/bash
process=monitor.py
makerun="/home/herbie/jetson/cpp-lidar/run_monitor.sh"

if ps ax | grep -v grep | grep $process > /dev/null
then
    exit
else
    $makerun &
fi

exit
