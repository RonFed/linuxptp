#!/bin/bash
ip link add dev wg0 type wireguard
ip addr add 10.0.0.3/24 dev wg0
wg setconf wg0 linuxptp/wireguard/configB.conf
ip link set wg0 up