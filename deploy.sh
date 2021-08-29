#!/bin/sh

mkdir -p _mysql_mount
mkdir -p logs
mkdir -p EventManager/logs
touch logs/debug.log
touch EventManager/logs/debug.log
sudo docker-compose up --build