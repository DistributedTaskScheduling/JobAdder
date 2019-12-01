#!/bin/bash

# All subdirectories of $1 which
# 1. Are not $1 itself
# 2. Are not hidden files
DIRECTORIES=$(find $1 ! -path $1 ! -path '*/\.*' -type d)

for d in $DIRECTORIES; do
    if [ -f $d/__init__.py ]; then
        continue
    fi
    echo "Directory $d does not contain a file __init__.py!"
    exit 1
done
