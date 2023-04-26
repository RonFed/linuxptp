from socket import *
from scapy.layers.l2 import Ether
from scapy.layers.inet import UDP, IP
import sys

args = sys.argv #[name, 10.0.0.1 eth0 10.0.0.2]
print(args)
PTP_EVENT_PORT = 319
es = socket(AF_INET, SOCK_DGRAM)

ip_addr = args[1] 
es.bind((ip_addr, 0))

with socket(AF_PACKET, SOCK_RAW, ntohs(0x0003)) as sock:
    sock.bind((args[2], 0))
    n_pkt = 0
    try:
        while True:
            raw_packet = sock.recv(1514)
            l2_pkt = Ether(raw_packet)
            if l2_pkt.haslayer(UDP) and l2_pkt[IP][UDP].dport == PTP_EVENT_PORT:
                b_ptp = l2_pkt[IP][UDP].load
                es.sendto(b_ptp, (args[3], 51820)) # Send packet over WG tunnel 
                n_pkt += 1

                # Send the original packet over the network
                sock2 = socket(AF_PACKET, SOCK_RAW)
                sock2.bind((args[2], 0))
                sock2.send(raw_packet)

    except Exception as e:
        print(e)
