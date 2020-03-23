#!/bin/bash
set -x
set -e

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root."
   exit 1
fi

PREFIX=/usr
SCRIPTPATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

# Install JobAdder source code + binaries
# FIXME: how to make setup.py ignore test folder??
cd $SCRIPTPATH
mv ./src/test/__init__.py ./src/test/init
mv ./src/ja_integration/__init__.py ./src/ja_integration/init
pip3 install ./src --prefix=$PREFIX
mv ./src/test/init ./src/test/__init__.py
mv ./src/ja_integration/init ./src/ja_integration/__init__.py

install ./data/bin/ja-server /usr/bin -m 755
install ./data/bin/ja-worker /usr/bin -m 755

# Install remote
install ./data/bin/ja-remote /usr/bin -m 755
chmod u+s /usr/bin/ja-remote

# Install suid-python helper
cd $SCRIPTPATH/data/suid-python-helper
make && make install
cd $SCRIPTPATH

# Install Systemd unit files
SERVER_SRV_FILE=/etc/systemd/system/JobAdderServer.service

cp ./data/bin/JobAdderServer.service $SERVER_SRV_FILE
chmod 644 $SERVER_SRV_FILE

# Install config file
CONFIG_FILE=/etc/jobadder/server.conf

if [ ! -f $CONFIG_FILE ]; then
    mkdir -p /etc/jobadder/
    install ./data/config-files/server.conf $CONFIG_FILE -m 644
fi
