import ipaddress

from Net.SwitchPort import SwitchPort


def is_gig_ethernet(version):
    if version == "2960" or version == "2960psl" or version == "2960ttl":
        return False
    else:
        return True


class SwitchInformation:

    def get_ethernet(self, eth):
        ethernet = f"fastEthernet {eth}"

        if self.is_gig:
            ethernet = f"gigabitEthernet 1/{eth}"

        return ethernet

    def __init__(self, **kwargs):
        self.id = kwargs.get('id', 0)
        self.console_com_port = kwargs.get('console_com_port', 'COM3')
        self.version = kwargs.get('version', '')
        self.is_gig = is_gig_ethernet(self.version)
        self.host_name = kwargs.get('host_name', '')
        self.username = kwargs.get('username', '')
        self.password = kwargs.get('password', '')
        self.ip_address = kwargs.get('ip_address', None)
        self.subnet = kwargs.get('subnet', '')
        self.network = kwargs.get('network', '')
        self.network_dhcp_subnet = kwargs.get('network_dhcp_subnet', '')
        self.dns = kwargs.get('dns', '')
        self.router = kwargs.get('router', '')
        self.start_vlan = kwargs.get('start_vlan', 0)
        self.start_ip = kwargs.get('start_ip', None)
        self.port_count = kwargs.get('port_count', 0)
        self.default_gateway = kwargs.get('default_gateway', 0)
        self.ports = []
        self.commands = []

        self.commands.append(f"interface range {self.get_ethernet(self.get_port_range())}")
        # self.commands.append("snmp trap mac-notification change added")
        self.commands.append("spanning-tree portfast")
        self.commands.append("spanning-tree bpduguard disable")
        self.commands.append("switchport mode access")
        self.commands.append(f"interface range gigabitEthernet0/1-2")
        self.commands.append("no spanning-tree portfast")
        self.commands.append("no switchport port-security")
        # self.commands.append("switchport trunk encapsulation dot1q")
        self.commands.append("switchport mode trunk")
        self.commands.append("switchport trunk allowed vlan all")
        self.commands.append(f"hostname {self.host_name}")
        self.commands.append("vlan " + str(int(self.start_vlan) - 1))
        self.commands.append("name management")
        self.commands.append("interface vlan " + str(int(self.start_vlan) - 1))
        self.commands.append("ip address " + str(self.ip_address) + " " + self.subnet)
        self.commands.append("no shutdown")
        self.commands.append("ip default-gateway " + self.default_gateway)
        # self.commands.append("snmp-server community private RW")
        # self.commands.append("snmp-server host 192.168.1.1 version 2c public mac-notification syslog port-security")
        # self.commands.append("no snmp-server enable traps snmp linkup")
        # self.commands.append("no snmp-server enable traps snmp linkdown")
        # self.commands.append("mac address-table notification change")
        # self.commands.append("snmp-server enable traps mac-notification change")
        # self.commands.append("snmp trap mac-notification change added")

        try:
            for p in range(int(self.port_count)):
                eth = '0/' + str(p + 1)
                vlan = str(int(self.start_vlan) + p)
                ip = ipaddress.ip_address(self.start_ip) + (p * 256)
                subnet = self.subnet
                network = ipaddress.ip_address(self.network) + (p * 256)
                network_dhcp_subnet = self.network_dhcp_subnet
                router = str(ipaddress.ip_address(self.router) + (p * 256))
                dns = self.dns
                username = self.username
                password = self.password
                sp = SwitchPort(eth=eth, vlan=vlan, ip=ip, subnet=subnet, network=network,
                                network_dhcp_subnet=network_dhcp_subnet, router=router, dns=dns, username=username,
                                password=password)
                cmds = sp.get_commands(self.is_gig)
                for c in cmds:
                    self.commands.append(c)
                self.ports.append(sp)
        except Exception as c:
            print("Error in generate_ports", c)

        print("all", len(self.ports), "port data generated successfully!")

    def get_all_commands(self):
        return self.commands

    def get_port_range(self):
        return "0/1" + "-" + str(self.port_count)
