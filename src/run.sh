#! /bin/bash

echo "Loading APs configuration..."

python main.py -i 111111 -s &
python main.py -i 222222 -s -f data/group2.txt &
python main.py -i 333333 -s -f data/group3.txt &
python main.py -i 444444 -s &
python main.py -i 555555 -s &
python main.py -i 666666 -s -f data/group1.txt &
python main.py -i 777777 -s -f data/group2.txt &
python main.py -i 888888 -s -f data/group3.txt &
python main.py -i 999999 -f data/group3.txt &
python main.py -i 000000 -s &
python main.py -i AAAAAA -s -f data/group4.txt &
python main.py -i BBBBBB -f data/group5.txt &
python main.py -i 111111 -f data/group6.txt &
python main.py -i 222222 -f data/group6.txt &
python main.py -i 222222 &
python main.py -i 333333 &
python main.py -i 444444 -f data/group5.txt &
python main.py -i CCCCCC -f data/group4.txt &
python main.py -i DDDDDD -f data/group4.txt &
python main.py -i EEEEEE -f data/group4.txt &
python main.py -i FFFFFF -s &
python main.py -i GGGGGG -s data/group2.txt &

echo "All APs loaded successfully"
echo "Running several APs..."

wait

