# FROM fedora:latest AS builder
# RUN dnf install git make gcc
# RUN git clone github.com/ron/ptp
# RUN make

# FROM fedora:latest
# COPY --from=builder /etc/ptp .


FROM fedora:latest As builder
RUN dnf -y install git-all make gcc dos2unix yum python3-pip iputils
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir netprotocols && \
    pip install --no-cache-dir scapy && \
    pip install --no-cache-dir gptp
