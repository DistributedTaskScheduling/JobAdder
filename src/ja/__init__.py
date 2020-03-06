"""
JobAdder is a software package for scheduling jobs on remote machines.
It has four sub-packages:
* user for components used exclusively on the user client.
* server for components used exclusively on the central server.
* worker for components used exclusively on the worker client.
* common for components used on at least two of: user client, central server,
  worker client.
"""
import logging
import os
# set JA_LOGLEVEL to DEBUG-> more info
# set JA_LOGLEVEL to INFO -> less info

LOGLEVEL = os.environ.get("JA_LOGLEVEL", "WARNING").upper()
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=LOGLEVEL)
