import time

from Net.CiscoHelper import CiscoSwitch


class SwitchConfiguration:
    def open(self):
        self.cisco_switch.connect()
        if not self.cisco_switch.connected:
            print(f"1.switch {self.info.console_com_port} can not connect, retry after {self.sleepTime} seconds")
            time.sleep(self.sleepTime)
            self.cisco_switch.connect()
            if not self.cisco_switch.connected:
                print(f"2.switch {self.info.console_com_port} can not connect, retry after {self.sleepTime} seconds")
                time.sleep(self.sleepTime)
                self.cisco_switch.connect()
                if not self.cisco_switch.connected:
                    print(
                        f"3.switch {self.info.console_com_port} can not connect, retry after {self.sleepTime} seconds")
                    time.sleep(self.sleepTime)
                    self.cisco_switch.connect()
                    if not self.cisco_switch.connected:
                        raise Exception("switch " + self.info.console_com_port + " can not connect")

    def close(self):
        self.cisco_switch.save()
        self.cisco_switch.exit_enable()
        self.cisco_switch.disconnect()

    def __init__(self, **kwargs):
        self.sleepTime = 6
        self.info = kwargs.get('information', '')
        self.commands = self.info.get_all_commands()
        self.cisco_switch = CiscoSwitch(self.info.console_com_port, self.info.is_gig)
        print("Trying to connect to switch on", self.info.console_com_port, "port")
        self.open()
        print("CONNECTED")
        self.cisco_switch.info()

    def setup2(self):
        try:
            for c in self.commands:
                print(c)
        except:
            print("ay")

        self.cisco_switch.setup_access_ports(self.info.get_port_range())
        print("start commit_all_commands")
        self.cisco_switch.commit_all_commands(self.commands)

    def setup_step_by_step(self):
        for port in self.info.ports:
            try:
                self.vlan_config(port)
                time.sleep(self.sleepTime)
            except Exception as c:
                print("Error in vlan_config for port " + str(port) + ":", c)
                return False

        time.sleep(self.sleepTime)
        print("All", len(self.info.ports), "ports has been configured")

        self.cisco_switch.setup_access_ports(self.info.get_port_range())
        print("setup_access_ports done")
        time.sleep(self.sleepTime)

        self.cisco_switch.setup_trunk_ports()
        print("setup_trunk_ports done")
        time.sleep(self.sleepTime)

        self.cisco_switch.set_hostname(self.info.host_name)
        print("set_hostname done")
        time.sleep(self.sleepTime)

        self.cisco_switch.set_management_vlan(int(self.info.start_vlan) - 1, self.info.ip_address, self.info.subnet,
                                              self.info.default_gateway)
        print("set_management_vlan done")
        time.sleep(self.sleepTime)

        self.cisco_switch.create_telnet_user(self.info.username, self.info.password)
        print("create_telnet_user done")
        time.sleep(self.sleepTime)

        self.close()

        return

    def vlan_config(self, port):
        pr = port.to_string()
        print(f"START vlan_config on {pr}")
        self.cisco_switch.enable_vlan(port.vlan, str(port.ip), port.subnet)
        time.sleep(self.sleepTime)
        self.cisco_switch.set_dhcp_pool(port.vlan, str(port.network) + ' ' + port.network_dhcp_subnet, port.dns,
                                        port.router)
        time.sleep(self.sleepTime)
        self.cisco_switch.config_interface(port.vlan, port.eth)
        print(f"COMPLETE vlan_config on {pr}")
