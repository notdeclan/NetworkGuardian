import socket

import psutil
from psutil._common import bytes2human

from networkguardian.framework.plugin import AbstractPlugin, PluginCategory, executor
from networkguardian.framework.registry import register_plugin


@register_plugin("Network Interface Information", PluginCategory.NETWORK, "Owen", 0.1)
class NetworkInterfaceInformation(AbstractPlugin):
    """
        This plugin will return details about the network interfaces. Such as whether the device is online or not, the IP, broadcast address, netmask and mac address.

        It will also display information about packets, speed, dropped packets and more.
    """

    @executor("template.html")
    def execute(self):
        """
        Using psutil it gathers all the information required and puts it all into a list so it
        can be used in the template to be displayed into a table.
        """
        af_map = {
            socket.AF_INET: 'IPv4',
            socket.AF_INET6: 'IPv6',
            psutil.AF_LINK: 'MAC',
        }

        duplex_map = {
            psutil.NIC_DUPLEX_FULL: "Full",
            psutil.NIC_DUPLEX_HALF: "Half",
            psutil.NIC_DUPLEX_UNKNOWN: "?",
        }

        main_list = {}

        stats = psutil.net_if_stats()
        io_counters = psutil.net_io_counters(pernic=True)
        for nic, addrs in psutil.net_if_addrs().items():
            st = stats[nic]
            io = io_counters[nic]

            main_list.update({nic: {
                "Speed": st.speed or "-",
                "Duplex": duplex_map[st.duplex] or "-",
                "MTU": st.mtu or "-",
                "up": st.isup or "False",
                "bytesin": bytes2human(io.bytes_recv) or "0",
                "packetsin": io.packets_recv or "0",
                "errorsin": io.errin or "0",
                "dropsin": io.dropin or "0",
                "bytesout": bytes2human(io.bytes_sent) or "0",
                "packetsout": io.packets_sent or "0",
                "errorsout": io.errout or "0",
                "dropsout": io.dropout or "0",
            }})

            for addr in addrs:
                key = af_map.get(addr.family, addr.family)
                if key == "MAC":
                    main_list[nic]["Mac"] = addr.address or "-"
                else:
                    key_broadcast = key + "Broadcast"
                    key_netmask = key + "Netmask"
                    main_list[nic][key_broadcast] = addr.address or "-"
                    main_list[nic][key_netmask] = addr.netmask or "-"

        return {"result": main_list}
