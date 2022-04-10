#!/bin/bash
x=1
while [ $x -gt 0 ]
do
	if [ $(($x%2)) -eq 0 ];
	then
		echo "changing to 5ghz"
		sudo ip link set wlan1 down
		sudo iw dev wlan1 set type monitor
		sudo iwconfig wlan1 channel 36
		sudo ip link set wlan1 up
	else
		echo "changing to 2.4ghz"
		sudo ip link set wlan1 down
		sudo iw dev wlan1 set type monitor
		sudo iwconfig wlan1 channel 1
		sudo ip link set wlan1 up
	fi

	sudo tcpdump -i wlan1 -c 240 -w capture$x.pcap
	tshark -V -r capture$x.pcap > ~/CACTUS/DB/capture/wifi/capture$x.txt
	rm -f capture$x.pcap
	x=$(( $x+1))
done
