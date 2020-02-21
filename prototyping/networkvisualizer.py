import ipaddress
import random
import socket
from contextlib import closing

import psutil
from icmplib import traceroute
from netaddr import IPNetwork
from nmap import nmap


class Tracer(object):
    def __init__(self, dst, hops=30):
        """
        Initializes a new tracer object

        Args:
            dst  (str): Destination host to probe
            hops (int): Max number of hops to probe

        """
        self.dst = dst
        self.hops = hops
        self.ttl = 1

        # Pick up a random port in the range 33434-33534
        self.port = random.choice(range(33434, 33535))

    def run(self):
        """
        Run the tracer

        Raises:
            IOError

        """
        try:
            dst_ip = socket.gethostbyname(self.dst)
        except socket.error as e:
            raise IOError('Unable to resolve {}: {}', self.dst, e)

        text = 'traceroute to {} ({}), {} hops max'.format(
            self.dst,
            dst_ip,
            self.hops
        )

        print(text)

        while True:
            receiver = self.create_receiver()
            sender = self.create_sender()
            sender.sendto(b'', (self.dst, self.port))

            addr = None
            try:
                data, addr = receiver.recvfrom(1024)
            except socket.error:
                raise IOError('Socket error: {}'.format(e))
            finally:
                receiver.close()
                sender.close()

            if addr:
                print('{:<4} {}'.format(self.ttl, addr[0]))
            else:
                print('{:<4} *'.format(self.ttl))

            self.ttl += 1

            if addr[0] == dst_ip or self.ttl > self.hops:
                break

    def create_receiver(self):
        """
        Creates a receiver socket

        Returns:
            A socket instance

        Raises:
            IOError

        """
        s = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_RAW,
            proto=socket.IPPROTO_ICMP
        )

        try:
            s.bind(('', self.port))
        except socket.error as e:
            raise IOError('Unable to bind receiver socket: {}'.format(e))

        return s

    def create_sender(self):
        """
        Creates a sender socket

        Returns:
            A socket instance

        """
        s = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_DGRAM,
            proto=socket.IPPROTO_UDP
        )

        s.setsockopt(socket.SOL_IP, socket.IP_TTL, self.ttl)

        return s


def get_networks():
    networks = []
    for interface_name, interfaces in psutil.net_if_addrs().items():
        for interface in interfaces:
            # Validate
            try:
                if ipaddress.ip_address(interface.address).is_loopback:  # if loopback
                    continue  # goto next one
            except ValueError:  # not valid ip address
                continue  # goto next one

            ipn = IPNetwork(f"{interface.address}/{interface.netmask}")
            print(f"Interface: {interface_name}")
            print("\tNetwork:", ipn[0])
            print("\tBroadcast:", ipn.broadcast)
            print("\tNetmask:", interface.netmask)
            print("\tCIDR:", ipn.cidr)
            print("\tNetbit", ipn._prefixlen)
            print("\tTotal IP's:", ipn.cidr.size)
            networks.append(ipn)

    return networks


def get_ip():
    """
    Finds and returns the local IP address as dotted-quad ints on my host computer.
    """
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.connect(("8.8.8.8", 53))
        ip = s.getsockname()[0]

    return ip


def pretty(d, indent=0):
    for key, value in d.items():
        print('\t' * indent + str(key))
        if isinstance(value, dict):
            pretty(value, indent + 1)
        else:
            print('\t' * (indent + 1) + str(value))


if __name__ == '__main__':
    all_networks = get_networks()
    nm = nmap.PortScanner()

    all_devices = []
    for network in all_networks:
        print("Scanning", network)
        nm.scan(str(network.cidr), arguments="-A -n")
        for host in nm.all_hosts():
            all_devices.append(nm[host])

        print("Finished Scanning", network)

    for device in all_devices:
        print("Gunna try traceroute ", device)
        for type, address in device['addresses'].items():
            if 'mac' in type:
                continue

            traceroute(address, count=3, interval=0.05, timeout=2, max_hops=30, fast_mode=False)
