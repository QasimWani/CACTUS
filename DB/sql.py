import sqlite3
from scapy.all import *

con = sqlite3.connect("data/local.db")
cur = con.cursor()

# create table if not exists
cur.execute(
    """CREATE TABLE IF NOT EXISTS wifi_capture
            (dnsrr text, source_ip text, destination_ip text)"""
)


capture = rdpcap("data/wifi_data.pcap")
# Let's iterate through every packet
for packet in capture:
    # We're only interested packets with a DNS Round Robin layer
    if packet.haslayer(DNSRR):
        # If the an(swer) is a DNSRR, print the name it replied with.
        if isinstance(packet.an, DNSRR):
            query = f"""INSERT INTO wifi_capture VALUES ('{bytes.decode(packet.an.rrname)}', '{packet.payload.src}', '{packet.payload.dst}')"""
            cur.execute(query)

con.commit()
con.close()

print("Done!")
