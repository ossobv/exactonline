#!/bin/sh

err=0

echo "--[ Python 2 ]--"
python2 -m unittest discover -v . '*.py' || err=1
echo

echo "--[ Python 3 ]--"
python3 -m unittest discover -v . '*.py' || err=1
echo

exit $err
