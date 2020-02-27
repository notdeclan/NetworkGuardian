import ipaddress
import random
import socket
import xml
from contextlib import closing

import networkx
import psutil
from libnmap.parser import NmapParser
from libnmap.process import NmapProcess
from netaddr import IPNetwork


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
    valid_networks = []
    for interface_name, interfaces in psutil.net_if_addrs().items():
        for interface in interfaces:
            try:
                # Validate Interface / Network
                assert not ipaddress.ip_address(interface.address).is_loopback  # if loopback
                assert not ipaddress.ip_address(interface.address).is_link_local  # if  link local
                assert psutil.net_if_stats()[interface_name].isup  # if disabled (down)
            except (AssertionError, ValueError):  # not valid ip address
                continue  # goto next one

            ipn = IPNetwork(f"{interface.address}/{interface.netmask}")

            print(f"Interface: {interface_name}")
            print("\tNetwork:", ipn[0])
            print("\tBroadcast:", ipn.broadcast)
            print("\tNetmask:", interface.netmask)
            print("\tCIDR:", ipn.cidr)
            print("\tNetbit", ipn._prefixlen)
            print("\tTotal IP's:", ipn.cidr.size)

            valid_networks.append(ipn)

    return valid_networks


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
    networks = get_networks()
    print(networks)

    for network in networks:
        print(str(network))
        nm1 = NmapProcess(str(network), options="-O -F -T5")
        nm1.run()
        parsed = NmapParser.parse(nm1.stdout)

        graph = networkx.Graph()
        nm2 = NmapProcess("google.com", options="--traceroute")
        nm2.run()

        collection = xml.etree.ElementTree.fromstring(nm2.stdout)
        nodes = collection.getiterator("hop")

        trace_list = []
        pre_node = ''

        for node in nodes:
            print(node)
            trace_list.append(node.attrib["ipaddr"])
            graph.add_node(node.attrib["ipaddr"])
            if pre_node != '':
                graph.add_edge(node.attrib["ipaddr"], pre_node)
            pre_node = node.attrib["ipaddr"]

        for host in parsed.hosts:
            if host.is_up():
                graph.add_node(host.address)
                if len(trace_list) > 0:
                    graph.add_edge(host.address, trace_list[0])

        data = networkx.json_graph.adjacency_data(graph)
        print(data)

    # nm = nmap.PortScanner()
    #
    # all_devices = []
    # for network in all_networks:
    #     # nm.scan(str(network.cidr), arguments="-A -n")  # correct args
    #     nm.scan(str(network.cidr), arguments="-sP")  # quick scan args
    #     for host in nm.all_hosts():
    #         all_devices.append(nm[host])
    #
    #     break  # just scan first network during testing
    #
    # print(all_devices)
    #
    # for device in all_devices:
    #     for type, address in device['addresses'].items():
    #         if 'mac' in type:
    #             continue
    #
    #         print("Gunna try traceroute ", address)
    #         hops = traceroute(address, count=3, interval=0.05, timeout=2, max_hops=30, fast_mode=True)
    #
    #         print(hops)
    #         print(dir(hops))
