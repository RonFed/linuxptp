from socket import *
from scapy.layers.l2 import Ether
from scapy.layers.inet import UDP, IP
import sys

args = sys.argv
print(args)
PTP_EVENT_PORT = 319
es = socket(AF_INET, SOCK_DGRAM)

# first arg is wireguard ip address of the machine running this script
# second arg is "real" ip of this machine
ip_addr = args[1]
#ip_addr = '10.0.0.1'
#ip_addr = get_ip_address(args.egress)

es.bind((ip_addr, 0))

# pp=RawPcapReader('a.pcap')
# p=pp.recv()
# l2_pkt = Ether(p)

with socket(AF_PACKET, SOCK_RAW, ntohs(0x0003)) as sock:
    sock.bind((args[2], 0))
    #sock.bind(('172.16.37.0', 0))
    n_pkt = 0
    try:
        while True:
            # for i in range (0,10):
            raw_packet = sock.recv(1514)
            print("a")
            # hexdump(raw_packet)
            l2_pkt = Ether(raw_packet)
            print("b")
            if l2_pkt.haslayer(UDP) and l2_pkt[IP][UDP].dport == PTP_EVENT_PORT:
                print("c")
                b_ptp = l2_pkt[IP][UDP].load
                print("d")
                # PTPv2(b_ptp).show()
                print(l2_pkt[IP].dst)
                es.sendto(b_ptp, (l2_pkt[IP].dst, PTP_EVENT_PORT))
                print("e")
                n_pkt += 1

    except Exception as e:
        print(e)
