# FROM fedora:latest AS builder
# RUN dnf install git make gcc
# RUN git clone github.com/ron/ptp
# RUN make

# FROM fedora:latest
# COPY --from=builder /etc/ptp .


FROM fedora:latest As builder
RUN dnf -y install git-all make gcc dos2unix yum python3-pip iputils net-tools iproute wireguard-tools
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir netprotocols && \
    pip install --no-cache-dir scapy && \
    #pip install --no-cache-dir gptp && \
    pip install --no-cache-dir wireguard


#ip link add dev wg0 type wireguard
#ip add add 10.0.0.1/24
#ip address add dev wg0 192.168.2.1/24
#ip address add dev wg0 192.168.2.1 peer 192.168.2.2
#wg setconf wg0 myconfig.conf
#ip link set up dev wg0