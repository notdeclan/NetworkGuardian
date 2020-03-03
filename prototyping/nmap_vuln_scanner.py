import ipaddress

import psutil
from netaddr import IPNetwork
from nmap import nmap


def get_networks():
    networks = {}
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
            networks[interface_name] = ipn

    return networks


if __name__ == '__main__':
    networks = get_networks()
    nm = nmap.PortScanner()
    for interface_name, interface in networks.items():
        interface_ip = str(interface.ip)
        print(interface_ip)
        result = nm.scan(interface_ip, arguments="-sV --script vuln")

        print("CMD", nm.command_line())
        print("Result", result)
        for host in nm.all_hosts():
            print("nm[host]", nm[host])
            print("Dir", dir(nm[host]))
