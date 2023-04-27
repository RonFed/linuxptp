import sys
from socket import *
from scapy.layers.l2 import Ether
from scapy.layers.inet import UDP, IP
from gptp.layers import PTPv2
from gptp.fields import TimestampField

PTP_EVENT_PORT = 319
WIREGUARD_LISTEN_PORT = 51820
PTP_INTERFACE_NAME = "eth0"

args = sys.argv

wg_endpoint_ip = "10.0.0.1"
wg_peer_endpoint_ip = "10.0.0.2"
local_ip = "172.16.37.0"

if ( args[1] == "1" ): # Second setup option
    wg_endpoint_ip = "10.0.0.2"
    wg_peer_endpoint_ip = "10.0.0.1"
    local_ip = "172.16.37.1"

# Initialize the WG endpoint socket
es = socket(AF_INET, SOCK_DGRAM) 
es.bind((wg_endpoint_ip, 0))

with socket(AF_PACKET, SOCK_RAW, ntohs(0x0003)) as sock:
    sock.bind((PTP_INTERFACE_NAME, 0))
    try:
        while True:
            raw_packet = sock.recv(1514)
            l2_pkt = Ether(raw_packet)

            # Catch out going PTP packets and send over WG tunnel
            if l2_pkt.haslayer('PTPv2'):
                if l2_pkt.haslayer(UDP) and l2_pkt[IP][UDP].dport == PTP_EVENT_PORT and l2_pkt[IP][UDP][PTPv2].reserved1 == 0:
                    l2_pkt[IP][UDP][PTPv2].reserved1 = 1
                    b_ptp = l2_pkt[IP][UDP].load
                    es.sendto(b_ptp, (wg_peer_endpoint_ip, PTP_EVENT_PORT)) # Send packet over WG tunnel 

                if l2_pkt[IP][UDP][PTPv2].reserved1 == 1:
                    print(l2_pkt.show())

    except Exception as e:
        print(e)
