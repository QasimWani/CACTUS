# Bluetooth Sniffing

## Dependency Setup

Install Tshark for processing PCAP files into TXT files

https://tshark.dev/setup/install/

`sudo apt-get install tshark`

## Ubertooth One Module Set Up on the Raspberry Pi 4 Model B

1. Set up a directory to hold the installation files and keep everything together and sorted:

```
mkdir ~/Ubertooth-One
cd ~/Ubertooth-One
```

2. Install the Ubertooth One files according to the Software "Building from git" page (not the "Build Guide" page):

https://ubertooth.readthedocs.io/en/latest/building_from_git.html

a) Follow the instructions under "Debian"

b) Follow the instructions under "libbtbb"

c) Navigate back to the Ubertooth One directory in Home ( `cd ~/Ubertooth-One` ), then follow the instructions under "Ubertooth Tools

3. This set up can be tested by going through the features show in the "Getting Started" page:

https://ubertooth.readthedocs.io/en/latest/getting_started.html

a) The `ubertooth-specan-ui` executable can be executed from anywhere in the file system, but it is worth noting that the executable file is stored in the `~/Ubertooth-One/ubertooth/host/python/specan_ui` directory

b) For LAP sniffing, the tools in libbtbb should already be compiled from the installation instructions in Step 2. The `ubertooth-rx` executable can be called from anywhere, but it is worth noting that the executable file is stored in the `~/Ubertooth-One/ubertooth/host/ubertooth-tools/src` directory

## Sniffing Bluetooth Packets Autonomously

There are two scripting files that are used in this project to autonomously sniff Bluetooth Low Energy (BTLE) packets and process the sniffed PCAP files into TXT files:

1. rotate_scan

`rotate_scan` will periodically start a new scan, sniffing all local BTLE packets and storing that information into a PCAP file before starting a new scan. All of these PCAP files will be stored in a single directory.

2. pcap_to_txt

As the file name states, `pcap_to_txt` will convert PCAP files to TXT files by using Tshark. The script does this by reading through the PCAP directory, searching for the first/last PCAP file in the directory, creating a TXT file from it, and then either deleting or archiving the PCAP file. The TXT file is stored in the Bluetooth capture directory in this repo so that they can be parsed into JSON file and stored in a Mongo database.
