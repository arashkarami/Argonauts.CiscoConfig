import ipaddress


def get_ethernet(is_gig, eth):
    ethernet = f"fastEthernet {eth}"

    if is_gig:
        ethernet = f"gigabitEthernet 1/{eth}"

    return ethernet


class SwitchPort:
    def __init__(self, **kwargs):
        self.eth = kwargs.get('eth', '')
        self.vlan = kwargs.get('vlan', '')
        self.ip = kwargs.get('ip', '')
        self.subnet = kwargs.get('subnet', '')
        self.network = kwargs.get('network', '')
        self.network_dhcp_subnet = kwargs.get('network_dhcp_subnet', '')
        self.dns = kwargs.get('dns', '')
        self.router = kwargs.get('router', '')
        self.username = kwargs.get('username', '')
        self.password = kwargs.get('password', '')

    def to_string(self):
        return "{etch:" + self.eth + ", vlan:" + str(self.vlan) + ",ip:" + str(self.ip) + ",network:" + str(
            self.network) + ",dns:" + self.dns + ",router:" + self.router + "}"

    def get_commands(self, is_gig):
        return [
            "vlan " + str(self.vlan),
            "ip dhcp excluded-address " + str(ipaddress.ip_address(self.network) + 3) + " " + str(
                ipaddress.ip_address(self.network) + 6),
            "interface vlan " + str(self.vlan),
            "ip address " + str(self.ip) + " " + str(self.subnet),
            "no shutdown",
            "ip dhcp pool " + str(self.vlan),
            "network " + str(self.network),
            "dns-server " + str(self.dns),
            "default-router " + str(self.router),
            f"interface {get_ethernet(is_gig, self.eth)}",
            "switchport access vlan " + str(self.vlan),
            "no shutdown"
        ]
