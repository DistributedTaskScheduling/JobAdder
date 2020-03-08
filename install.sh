#!/bin/bash

PREFIX=/usr

# Install JobAdder source code + binaries
# FIXME: how to make setup.py ignore test folder??
mv ./src/test/__init__.py ./src/test/init
./src/setup.py install --prefix=$PREFIX
mv ./src/test/init ./src/test/__init__.py

# TODO: when remote is ready, set SUID

# Install Systemd unit files
cp src/bin/JobAdderServer.service /etc/systemd/system/
