from scapy.all import *
from gptp.layers import PTPv2

def packet_callback(packet):
    if packet.haslayer('PTPv2'):
        print(packet.show())

sniff(prn=packet_callback, count=1000)

