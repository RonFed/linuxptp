import sys
import threading
from socket import *
from scapy.all import sniff
from scapy.layers.l2 import Ether
from scapy.layers.inet import UDP, IP
from gptp.layers import PTPv2

PTP_EVENT_PORT          = 319
WIREGUARD_LISTEN_PORT   = (21841 if sys.argv[1] == "0" else 41414)
PTP_INTERFACE_NAME      = "eth0"
WG_ENDPOINT_IP, WG_PEER_ENDPOINT_IP, LOCAL_IP = (
    ("10.0.0.1", "10.0.0.2", "172.16.37.0") if sys.argv[1] == "0" else
    ("10.0.0.2", "10.0.0.1", "172.16.37.1")   
)

def handle_packet(packet):
    print(packet.show())

def pass_ptp_packets_to_wg(recv_socket, stop_event):
    forward_socket = socket(AF_INET, SOCK_DGRAM) 
    forward_socket.bind((WG_ENDPOINT_IP, 0))
    
    try:
        while not stop_event.is_set():
            raw_packet = recv_socket.recv(1514)
            l2_pkt = Ether(raw_packet)
            
            # Catch out going PTP packets and send over WG tunnel
            if l2_pkt.haslayer(UDP) and l2_pkt.haslayer('PTPv2'):
                if l2_pkt[IP][UDP].dport == PTP_EVENT_PORT and l2_pkt[IP][UDP][PTPv2].reserved1 == 0:
                    l2_pkt[IP][UDP][PTPv2].reserved1 = 1
                    b_ptp = l2_pkt[IP][UDP].load
                    forward_socket.sendto(b_ptp, (WG_PEER_ENDPOINT_IP, WIREGUARD_LISTEN_PORT)) # Send packet over WG tunnel 
            
    except Exception as e:
        print(e)

def pass_wg_packets_to_ptp(recv_socket, stop_event):
    #forward_socket = socket(AF_INET, SOCK_DGRAM) 
    #forward_socket.bind((LOCAL_IP, 0))

    try:
        while not stop_event.is_set():
            raw_packet = recv_socket.recv(1514)
            l2_pkt = Ether(raw_packet)
            print(l2_pkt.show())
            if l2_pkt.haslayer(UDP) and l2_pkt.haslayer(IP) and l2_pkt[IP][UDP].dport == 51820:
                b_ptp = l2_pkt[IP][UDP].load
                #forward_socket.sendto(b_ptp, (LOCAL_IP, PTP_EVENT_PORT)) 

    except Exception as e:
        print(e)


# create two sockets for receiving packets
ptp_recv_socket = socket(AF_PACKET, SOCK_RAW, ntohs(0x0003))
ptp_recv_socket.bind((PTP_INTERFACE_NAME, 0))

#wg_recv_socket = socket(AF_INET, SOCK_STREAM) 
wg_recv_socket = socket(AF_INET, SOCK_DGRAM)
#wg_recv_socket = socket(AF_PACKET, SOCK_RAW, ntohs(0x0003))
wg_recv_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
wg_recv_socket.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
print(LOCAL_IP, WG_ENDPOINT_IP, WIREGUARD_LISTEN_PORT)
wg_recv_socket.bind((LOCAL_IP, WIREGUARD_LISTEN_PORT))

# create stop events for the two threads
stop_event1 = threading.Event()
stop_event2 = threading.Event()

# create two threads for receiving packets on the two sockets
t1 = threading.Thread(target=pass_ptp_packets_to_wg, args=(ptp_recv_socket, stop_event1))
t2 = threading.Thread(target=pass_wg_packets_to_ptp, args=(wg_recv_socket, stop_event2))

# start the two threads
t1.start()
t2.start()

# wait for the threads to finish
try:
    while True:
        pass
except KeyboardInterrupt:
    print("Terminating threads...")
    stop_event1.set()
    stop_event2.set()

# wait for the threads to finish
t1.join()
t2.join()
