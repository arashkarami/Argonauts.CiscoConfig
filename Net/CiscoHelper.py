import time

from netmiko import ConnectHandler

from Net.Network import mac_normalize, port_name
from Net.RedisHelper import RedisManager, get_bulk, insert_single_list


class Cisco:
    def __init__(self):
        self.core_devices = ["C1", "C2", "C3", "C4"]
        self.access_devices = ["S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8", "S9", "S10", "S11", "S12", "S13", "S14",
                               "S15", "S16", "S17", "S18", "S19", "S20", "S21", "S22", "S23", "S24", "S25", "S26",
                               "S27", "S28", "S29", "S30", "S31", "S32", "S33", "S34", "S35", "S36", "S37"]
        self.core_switches = []
        self.access_switches = []
        self.found_core_switches = []
        self.found_access_switches = []
        self.redis = RedisManager()

    def get_all_dhcp_clients(self):
        return get_bulk(self.redis.mikrotik)

    def filter_devices(self, dhcp_clients):
        for mac, info in dhcp_clients.items():
            try:
                if 'active-client-id' in info.keys() and 'cisco' in info['active-client-id']:
                    if 'host-name' in info.keys():
                        if info['host-name'] in self.core_devices:
                            self.core_switches.append(info)
                            self.found_core_switches.append(info['host-name'])
                        elif info['host-name'] in self.access_devices:
                            self.access_switches.append(info)
                            self.found_access_switches.append(info['host-name'])
                        else:
                            try:
                                insert_single_list(self.redis.lists, "UNKNOWN_CISCO", info)
                                print("Unknown cisco device found : ", info)
                            except Exception as c:
                                print("Error in inserting unknown cisco device : ", c)
                                pass
                    else:
                        try:
                            insert_single_list(self.redis.lists, "UNKNOWN_CISCO", info)
                            print("Unknown cisco device found : ", info)
                        except Exception as c:
                            print("Error in inserting unknown cisco device : ", c)
                            pass
            except Exception as c:
                print(c)
                pass


class CiscoSwitch:
    def __init__(self, com_port="COM13", is_gig=False):
        self.com_port = com_port
        self.is_gig = is_gig
        self.cisco_device = {
            'device_type': 'cisco_ios_serial',
            'username': 'frox',
            'password': 'Fr0xplus',
            'conn_timeout': 5000,
            'auth_timeout': 5000,
            'banner_timeout': 5000,
            'blocking_timeout': 5000,
            'session_timeout': 5000,
            'timeout': 5000,
            'serial_settings': {
                'port': com_port,
                # 'baudrate': 9600,
                # 'bytesize': serial.EIGHTBITS,
                # 'parity': serial.PARITY_NONE,
                # 'stopbits': serial.STOPBITS_ONE,
            }
        }

        self.interface_status = None
        self.mac_address_table = None
        self.port_status = {}
        self.port_mac = {}
        self.interface_summary = {}
        self.net_connect = None
        self.connected = False
        self.serial = None
        self.hostname = None
        self.version = None
        self.model = None
        self.mac = None
        self.number_of_ports = None

    def connect(self):
        try:
            self.net_connect = ConnectHandler(**self.cisco_device)
            self.enable()
            self.connected = True
            # self.connected = self.net_connect.is_alive()
            return True
        except Exception as c:
            print("Error in connect: ", c)
            return False

    def disconnect(self):
        try:
            self.net_connect.disconnect()
            self.connected = False
            self.connected = self.net_connect.is_alive()
            if self.connected:
                self.net_connect.disconnect()
                self.connected = False

            time.sleep(1)
        except:
            self.connected = None

    def check_enable(self):
        return self.net_connect.check_enable_mode()

    def enable(self):
        try:
            if not self.check_enable():
                self.net_connect.enable()
        except:
            pass

    def exit_enable(self):
        try:
            if self.check_enable():
                self.net_connect.exit_enable_mode()
        except:
            pass

    def check_config(self):
        return self.net_connect.check_config_mode()

    def config(self):
        try:
            if not self.check_config():
                self.net_connect.config_mode()
        except:
            pass

    def exit_config(self):
        try:
            if self.check_config():
                self.net_connect.exit_config_mode()
        except:
            pass

    def save(self):
        return self.net_connect.save_config()

    def reload(self):
        self.net_connect.send_command_timing(command_string='reload', strip_prompt=False, strip_command=False)
        self.net_connect.send_command_timing(self.net_connect.RETURN, strip_prompt=False, strip_command=False)

    def erase(self):
        self.net_connect.send_command_timing(command_string='erase startup-config', strip_prompt=False,
                                             strip_command=False)
        self.net_connect.send_command_timing(self.net_connect.RETURN, strip_prompt=False, strip_command=False)
        self.net_connect.send_command_timing(command_string='del flash:vlan.dat', strip_prompt=False,
                                             strip_command=False)
        self.net_connect.send_command_timing(self.net_connect.RETURN, strip_prompt=False, strip_command=False)
        self.reload()

    def info(self):
        output = self.net_connect.send_command('show version', use_textfsm=True)
        cisco_data = output[0]
        self.serial = cisco_data["serial"][0]
        self.hostname = cisco_data["hostname"]
        self.version = cisco_data["version"]
        self.model = cisco_data["hardware"][0]
        self.mac = cisco_data["mac"][0]
        self.number_of_ports = 24 if "24" in self.model else 48

    def get_interfaces_status(self):
        self.interface_status = self.net_connect.send_command('show int status', use_textfsm=True)
        for interface in self.interface_status:
            self.port_status[interface['port']] = interface['status']

    def get_interfaces_status_raw(self):
        return self.net_connect.send_command('show int status')

    def get_mac_address_table(self):
        self.mac_address_table = self.net_connect.send_command('show mac address-table', use_textfsm=True)
        for info in self.mac_address_table:
            if info['destination_port'] in self.port_mac.keys():
                self.port_mac[info['destination_port']].append(mac_normalize(info['destination_address']))
            else:
                self.port_mac[info['destination_port']] = [mac_normalize(info['destination_address'])]
            self.port_mac[info['destination_port']] = list(set(self.port_mac[info['destination_port']]))

    def clear_mac_address_table(self):
        self.net_connect.send_command('clear mac address-table dynamic')

    def shut_port(self, port):
        try:
            config_command = ["interface " + str(port), "shutdown"]
            shutdown_output = self.net_connect.send_config_set(config_command)
            return True
        except Exception as c:
            print("Error in shhut port : ", c)
            return False

    def no_shut_port(self, port):
        try:
            config_command = ["interface " + str(port), "no shutdown"]
            shutdown_output = self.net_connect.send_config_set(config_command)
            return True
        except Exception as c:
            print("Error in no shut port : ", c)
            return False

    def generate_interface_summary(self):
        self.get_interfaces_status()
        self.get_mac_address_table()
        for port, status in self.port_status.items():
            self.interface_summary[port_name(self.hostname, port)] = {
                "status": status,
                "mac": self.port_mac[port] if port in self.port_mac.keys() else [],
                "interface": port
            }
        return self.interface_summary

    def enable_vlan(self, vlan, ip, subnet):
        commands = [
            "vlan " + str(vlan),
            # "interface vlan " + str(vlan),
            # "ip address " + ip + " " + subnet,
            # "no shutdown"
        ]

        try:
            commands_output = self.net_connect.send_config_set(commands)
            print(commands_output)
            return True
        except Exception as c:
            print("Error in enabling vlan " + str(vlan) + ":", c)
            return False

    def commit_all_commands(self, commands):
        try:
            commands_output = self.net_connect.send_config_set(commands)
            print(commands_output)
            return True
        except Exception as c:
            print("Error in commit_all_commands:", c)
            return False

    def set_management_vlan(self, vlan, ip, subnet, default_gateway):
        commands = [
            "vlan " + str(vlan),
            "name management",
            "interface vlan " + str(vlan),
            "ip address " + str(ip) + " " + subnet,
            "no shutdown",
            "ip default-gateway " + default_gateway
        ]
        print(commands)
        try:
            commands_output = self.net_connect.send_config_set(commands)
            print(commands_output)
            return True
        except Exception as c:
            print("Error in enabling vlan " + str(vlan) + ":", c)
            return False

    def set_dhcp_pool(self, vlan, network, dns, router):
        commands = [
            "ip dhcp pool " + str(vlan),
            "network " + network,
            "dns-server " + dns,
            "default-router " + router
        ]
        try:
            commands_output = self.net_connect.send_config_set(commands)
            print(commands_output)
            return True
        except Exception as c:
            print("Error in set_dhcp_pool for vlan " + str(vlan) + ":", c)
            return False

    def get_ethernet(self, eth):
        ethernet = f"fastEthernet {eth}"

        if self.is_gig:
            ethernet = f"gigabitEthernet 1/{eth}"

        return ethernet

    def config_interface(self, vlan, eth):
        commands = [
            # "enable",
            # "configure terminal",
            f"interface {self.get_ethernet(eth)}",
            "switchport access vlan " + str(vlan),
            "no shutdown"
        ]
        try:
            commands_output = self.net_connect.send_config_set(commands)
            print(commands_output)
            return True
        except Exception as c:
            print("Error in config_interface for vlan " + str(vlan) + ":", c)
            return False

    def enable_vlan_dhcp(self):
        commands = [
            "mac address-table aging-time 300 vlan 1",
            "Interface Vlan 1",
            "shutdown"
            "ip address dhcp",
            "no shutdown"
        ]
        try:
            commands_output = self.net_connect.send_config_set(commands)
            print(commands_output)
            return True
        except Exception as c:
            print("Error in enabling vlan 1 DHCP : ", c)
            return False

    def set_hostname(self, hostname):
        commands = [
            f"hostname {hostname}"
        ]
        try:
            commands_output = self.net_connect.send_config_set(commands)
            print(commands_output)
            return True
        except Exception as c:
            print("Error in setting hostname : ", c)
            return False

    def enable_auto_revocer_errors(self):
        commands = [
            "errdisable recovery cause all",
            "errdisable recovery interval 30",
        ]
        try:
            commands_output = self.net_connect.send_config_set(commands)
            print(commands_output)
            return True
        except Exception as c:
            print("Error in enabling auto recovery : ", c)
            return False

    def setup_access_ports(self, port_range):
        commands = [
            f"interface range {self.get_ethernet(port_range)}",
            "spanning-tree portfast",
            "spanning-tree bpduguard disable",
            "switchport mode access",
        ]
        try:
            commands_output = self.net_connect.send_config_set(commands)
            print(commands_output)
            return True
        except Exception as c:
            print("Error in setting up access ports : ", c)
            return False

    def setup_access_ports_with_port_security(self, port_range):
        commands = [
            f"interface range {self.get_ethernet(port_range)}",
            "spanning-tree portfast",
            "spanning-tree bpduguard disable",
            "switchport port-security",
            "switchport mode access",
            "switchport port-security maximum 1",
            "switchport port-security violation shutdown",
            "switchport port-security mac-address sticky",
            "switchport port-security",
        ]
        try:
            commands_output = self.net_connect.send_config_set(commands)
            print(commands_output)
            return True
        except Exception as c:
            print("Error in setting up access ports : ", c)
            return False

    def setup_trunk_ports(self):
        commands = [
            f"interface range gigabitEthernet0/1-2",
            "no spanning-tree portfast",
            "spanning-tree bpduguard enable",
            "no switchport port-security",
            "switchport trunk encapsulation dot1q",
            "switchport mode trunk",
            "switchport trunk allowed vlan all",
        ]
        try:
            commands_output = self.net_connect.send_config_set(commands)
            print(commands_output)
            return True
        except Exception as c:
            print("Error in setting up trunk ports : ", c)
            return False

    def create_telnet_user(self, username="frox", password="Fr0xplus"):
        commands = [
            f"username {username} privilege 15 secret {password}",
            "line vty 0 15",
            "login local",
        ]
        try:
            commands_output = self.net_connect.send_config_set(commands)
            print(commands_output)
            return True
        except Exception as c:
            print("Error in creating telnet user : ", c)
            return False
#
# def get_no_power_devices(ip, hostname):
#     redis_con = redis.Redis(
#         host='localhost',
#         port=6379,
#         db=1)
#     redis_con2 = redis.Redis(
#         host='localhost',
#         port=6379)
#     cisco_device = {
#         'device_type': 'cisco_ios_telnet',
#         'host': ip,
#         'username': 'frox',
#         'password': 'Fr0xplus',
#     }
#     net_connect = ConnectHandler(**cisco_device)
#     net_connect.send_command("terminal length 0")
#     output = net_connect.send_command('show version', use_textfsm=True)
#     version_info = json.dumps(output, indent=2)
#     # print(output[0]["hardware"][0])
#     model = output[0]["hardware"][0]
#
#     # output = net_connect.send_config_set(
#     #     [
#     #         "interface range Fa0/1-45",
#     #         'spanning-tree portfast',
#     #         "no shut"
#     #     ]
#     # )
#     # print(output)
#     # number_of_ports = 24 if "24" in output[0]["hardware"][0] else 48
#     # channel_number = 0
#     # for i in range(1, number_of_ports+1):
#     #     channel_number += 1
#     #     print("no interface port-channel {}".format(i))
#     #     output = net_connect.send_config_set(
#     #         [
#     #             "no interface port-channel {}".format(i),
#     #         ]
#     #     )
#     #     print(output)
#     # output = net_connect.send_config_set(
#     #     [
#     #         "no interface port-channel {}".format(channel_number),
#     #         "interface range g1/0/{}-{}".format(i, i + 1),
#     #         'channel-protocol lacp',
#     #         "channel-group {} mode active".format(channel_number),
#     #         "no shut"
#     #     ]
#     # )
#     # print(output)
#     #
#     # output = net_connect.send_config_set(
#     #     [
#     #         "interface port-channel {}".format(channel_number),
#     #         '#switchport mode access',
#     #         '#switchport access vlan 1',
#     #         "no shut"
#     #     ]
#     # )
#     # print(output)
#
#     interface_status = net_connect.send_command('show int status', use_textfsm=True)
#     # print(json.dumps(interface_status, indent=2))
#     for interface in interface_status:
#         if model in switch_F:
#             if "G" in interface["port"]:
#                 continue
#         port = str(interface["port"]).split("/")[-1]
#         status = True if interface["status"] == "connected" else False
#         port_name = "{}-{}".format(hostname, port)
#         if port_name in all_devices.keys():
#             if not status:
#                 print("{}-{} -> {} : {} (PORT OFF)".format(hostname, port, all_devices[port_name],
#                                                            "OK" if status else "FAIL"))
#
#     mac_table = net_connect.send_command('show mac address-table', use_textfsm=True)
#     # print(json.dumps(mac_table, indent=2))
#     mac_port = {}
#     for interface in mac_table:
#         # print(interface)
#         if model in switch_F:
#             if "Gi" in interface["destination_port"]:
#                 continue
#         if "CPU" in interface["destination_port"]:
#             continue
#         port = str(interface["destination_port"]).split("/")[-1]
#         mac = mac_normalize(interface["destination_address"])
#         port_name = "{}-{}".format(hostname, port)
#         if port_name not in all_devices.keys():
#             continue
#         redis_con2.set(str(mac), str(all_devices[port_name]))
#         # print(str(mac), str(all_devices[port_name]))
#         if not redis_con.exists(mac):
#             print("{}-{} -> {} : {} (MAC LOOKUP FAILED) {}".format(hostname, port, all_devices[port_name],
#                                                                    "FAIL", mac))
#         # mac_port[port_name] = mac_normalize(mac)
#         miner_ip = mac_ip[mac]
#         for miner_port in check_ports:
#             if not isOpen(miner_ip, miner_port):
#                 print("{} : {}-> FAIL (PORT CHECK FAILED)".format(all_devices[port_name], miner_ip))
