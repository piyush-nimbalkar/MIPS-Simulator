#!/bin/bash

if [ "$#" == 0 ]; then
  python simulator.py inst.txt data.txt reg.txt config.txt result.txt
  exit 0
fi


if [ "$#" -ne 5 ]; then
  echo "Usage: $0 inst.txt data.txt reg.txt config.txt result.txt" >&2
  exit 1
fi

python simulator.py $1 $2 $3 $4 $5
