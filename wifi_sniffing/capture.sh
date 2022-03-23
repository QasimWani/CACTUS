#!/bin/bash
x=1
while [ $x -gt 0 ]
do
	sudo tcpdump -i wlan1 -c 240 -w capture$x.pcap
	tshark -V -r capture$x.pcap > ~/wificaptures/capture$x.txt
	x=$(( $x+1))
done
