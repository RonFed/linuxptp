import sys
import threading
import base64
from socket import *
from scapy.all import sniff
from scapy.layers.l2 import Ether
from scapy.layers.inet import UDP, IP
from gptp.layers import PTPv2

PTP_EVENT_PORT          = 319
WG_PORT                 = 500
PTP_INTERFACE_NAME      = "eth0"
WG_ENDPOINT_IP, WG_PEER_ENDPOINT_IP, LOCAL_IP = (
    ("10.0.0.1", "10.0.0.2", "172.16.37.0") if sys.argv[1] == "0" else
    ("10.0.0.2", "10.0.0.1", "172.16.37.1")   
)

def pass_ptp_packets_to_wg():
    ptp_recv_socket = socket(AF_PACKET, SOCK_RAW, ntohs(0x0003))
    ptp_recv_socket.bind((PTP_INTERFACE_NAME, 0))
    forward_socket = socket(AF_INET, SOCK_DGRAM) 
    forward_socket.bind((WG_ENDPOINT_IP, 0))
    
    try:
        while True:
            raw_packet = ptp_recv_socket.recv(1514)
            l2_pkt = Ether(raw_packet)
            
            # Catch out going PTP packets and send over WG tunnel
            if l2_pkt.haslayer(UDP) and l2_pkt.haslayer('PTPv2'):
                if l2_pkt[IP].src == LOCAL_IP and l2_pkt[IP][UDP].dport == PTP_EVENT_PORT and l2_pkt[IP][UDP][PTPv2].reserved1 == 0:
                    l2_pkt[IP][UDP][PTPv2].reserved1 = 1
                    b_ptp = l2_pkt[IP][UDP][PTPv2]
                    forward_socket.sendto(bytes(b_ptp), (WG_PEER_ENDPOINT_IP, WG_PORT)) # Send packet over WG tunnel 

    except Exception as e:
        print(e)

if __name__=='__main__':
    pass_ptp_packets_to_wg()