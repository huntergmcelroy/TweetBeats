#!/bin/bash
cd MIDIUtil-0.89
python setup.py install
echo "MIDIUtil installed!"
pip install pygame
echo "pygame installed!"
pip install boto
echo "boto installed!"
pip install tweepy
echo "tweepy installed!"
echo "ALL DEPENDENCIES INSTALLED SUCCESSFULLY"