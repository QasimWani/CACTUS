import pyshark
import time

local = time.localtime()
filename = "test_" + str(local.tm_year) + "-" + str(local.tm_mon) + "-" + str(local.tm_mday)
filename += "_" + str(local.tm_hour) + "-" + str(local.tm_min) + "-" + str(local.tm_sec) + ".txt"
filename = "test"

# Set pyshark to do a live capture of packets on a specific interface
capture = pyshark.LiveCapture(interface='bluetooth0', output_file=filename)

# Sniff to capture for a certain amount of time
print("Live capturing for 30 seconds")
capture.sniff(timeout=30)
print("Done capturing")
print(str(len(capture)))
if len(capture) == 0:
    print("No packets")
else:
    i = 0
    while (i < len(capture)):
        print(capture[i])
        i += 1
#     for packet in capture:
#         print("Packet:", packet)

# Sniff to capture certain amount of packets and perform an action on each packet
# print("Live capturing until 10 packets are received")
# print("Print as packets are received")
# for packet in capture.sniff_continuously(packet_count=10):
#     print('Just arrived:', packet)