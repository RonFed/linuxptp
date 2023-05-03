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
                if l2_pkt[IP].src == LOCAL_IP and l2_pkt[IP][UDP].dport == PTP_EVENT_PORT and l2_pkt[IP][UDP][PTPv2].reserved1 == 0:
                    l2_pkt[IP][UDP][PTPv2].reserved1 = 1
                    #b_ptp = l2_pkt[IP][UDP][PTPv2].load
                    #b_ptp = "ABC".encode('ascii')
                    bytes_sent = forward_socket.sendto(bytes(l2_pkt), (WG_PEER_ENDPOINT_IP, WG_PORT)) # Send packet over WG tunnel 
                    #print(f"Sent {bytes_sent} bytes over WG tunnel")

    except Exception as e:
        print(e)

def pass_wg_packets_to_ptp(recv_socket, stop_event):
    forward_socket = socket(AF_INET, SOCK_DGRAM) 
    forward_socket.bind((LOCAL_IP, 0))

    try:
        while not stop_event.is_set():
            raw_packet = recv_socket.recv(1514)
            print(f"Recived: {Ether(raw_packet)[IP][UDP][PTPv2].reserved1}")
            b_ptp = Ether(raw_packet)[IP][UDP][PTPv2]
            bytes_sent = forward_socket.sendto(bytes(b_ptp), (LOCAL_IP, PTP_EVENT_PORT)) 
            #print(f"Sent {bytes_sent} bytes to ptp4l")

    except Exception as e:
        print(e)


# create two sockets for receiving packets
ptp_recv_socket = socket(AF_PACKET, SOCK_RAW, ntohs(0x0003))
ptp_recv_socket.bind((PTP_INTERFACE_NAME, 0))

# wg_recv_socket = socket(AF_INET, SOCK_DGRAM)
# wg_recv_socket.bind((WG_ENDPOINT_IP, WG_PORT))
# print(f'Listening on {WG_PEER_ENDPOINT_IP}:{WG_PORT}')

# create stop events for the two threads
stop_event1 = threading.Event()
#stop_event2 = threading.Event()

# create two threads for receiving packets on the two sockets
t1 = threading.Thread(target=pass_ptp_packets_to_wg, args=(ptp_recv_socket, stop_event1))
#t2 = threading.Thread(target=pass_wg_packets_to_ptp, args=(wg_recv_socket, stop_event2))

# start the two threads
t1.start()
#t2.start()

# wait for the threads to finish
try:
    while True:
        pass
except KeyboardInterrupt:
    print("Terminating threads...")
    stop_event1.set()
 #   stop_event2.set()

# wait for the threads to finish
t1.join()
#t2.join()
