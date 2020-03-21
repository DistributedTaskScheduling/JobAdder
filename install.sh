#!/bin/bash

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root."
   exit 1
fi

PREFIX=/usr
SCRIPTPATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

# Install JobAdder source code + binaries
# FIXME: how to make setup.py ignore test folder??
cd $SCRIPTPATH/src/
mv ./test/__init__.py ./test/init
./setup.py install --prefix=$PREFIX
mv ./test/init ./test/__init__.py
cd $SCRIPTPATH

# TODO: when remote is ready, set SUID

# Install Systemd unit files
SERVER_SRV_FILE=/etc/systemd/system/JobAdderServer.service

cp ./data/bin/JobAdderServer.service $SERVER_SRV_FILE
chmod 644 $SERVER_SRV_FILE

# Install config file
CONFIG_FILE=/etc/jobadder/server.conf

if [ ! -f $CONFIG_FILE ]; then
    mkdir -p /etc/jobadder/
    cp ./data/config-files/server.conf $CONFIG_FILE
    chmod 644 $CONFIG_FILE
fi
