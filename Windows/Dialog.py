from Net.SwitchConfiguration import SwitchConfiguration
from Net.SwitchInformation import SwitchInformation

from guizero import App, Text, TextBox, PushButton


class SwitchDialog:
    def on_click_button(self):
        self.result_label.value = self.id_Text.value + " Starting configuration process ..."

        try:
            self.id_Text.value = '1'
            self.com_port_Text.value = 'COM5'
            self.version_Text.value = '2960'
            self.host_name_Text.value = 'frox'
            self.username_Text.value = 'frox'
            self.password_Text.value = 'froxplus'
            self.ip_address_Text.value = '192.168.100.1'
            self.subnet_Text.value = '255.255.255.0'
            self.network_Text.value = '192.168.101.0'
            self.network_dhcp_subnet_Text.value = '/29'
            self.dns_Text.value = '8.8.8.8'
            self.router_Text.value = '192.168.101.1'
            self.start_vlan_Text.value = '101'
            self.start_ip_Text.value = '192.168.101.6'
            self.port_count_Text.value = 24
            self.default_gateway_Text.value = "192.168.100.254"

            switch_info = SwitchInformation(id=self.id_Text.value,
                                            console_com_port=self.com_port_Text.value,
                                            version=self.version_Text.value,
                                            host_name=self.host_name_Text.value,
                                            username=self.username_Text.value,
                                            password=self.password_Text.value,
                                            ip_address=self.ip_address_Text.value,
                                            subnet=self.subnet_Text.value,
                                            network=self.network_Text.value,
                                            network_dhcp_subnet=self.network_dhcp_subnet_Text.value,
                                            dns=self.dns_Text.value,
                                            router=self.router_Text.value,
                                            start_vlan=self.start_vlan_Text.value,
                                            start_ip=self.start_ip_Text.value,
                                            port_count=self.port_count_Text.value,
                                            default_gateway=self.default_gateway_Text.value)

            switch = SwitchConfiguration(information=switch_info)

            switch.setup2()

            print("FINISH ALL SUCCESSFULLY")
            self.result_label.value = self.id_Text.value + " has been configured successfully"
        except Exception as c:
            self.result_label.color = "#ff0000"
            self.result_label.value = "ERROR", c
            print(c)

    def on_change_text_event(self):
        self.result_label.value = "waiting for enter..."

    def __init__(self):
        """Initializer."""
        self.app = App(title="Switch configuration", width=800, height=800)
        self.id_label = Text(self.app, text="Switch-id")
        self.id_Text = TextBox(self.app, 0, 50)
        self.id_Text.when_clicked = self.on_change_text_event

        self.com_port_label = Text(self.app, text="com_port")
        self.com_port_Text = TextBox(self.app, 0, 50)

        self.version_label = Text(self.app, text="version")
        self.version_Text = TextBox(self.app, 0, 50)

        self.host_name_label = Text(self.app, text="host_name")
        self.host_name_Text = TextBox(self.app, 0, 50)

        self.username_label = Text(self.app, text="username")
        self.username_Text = TextBox(self.app, 0, 50)

        self.password_label = Text(self.app, text="password")
        self.password_Text = TextBox(self.app, 0, 50)

        self.ip_address_label = Text(self.app, text="ip_address")
        self.ip_address_Text = TextBox(self.app, 0, 50)

        self.subnet_label = Text(self.app, text="subnet")
        self.subnet_Text = TextBox(self.app, 0, 50)

        self.network_label = Text(self.app, text="network")
        self.network_Text = TextBox(self.app, 0, 50)

        self.network_dhcp_subnet_label = Text(self.app, text="network_dhcp_subnet")
        self.network_dhcp_subnet_Text = TextBox(self.app, 0, 50)

        self.dns_label = Text(self.app, text="dns")
        self.dns_Text = TextBox(self.app, 0, 50)

        self.router_label = Text(self.app, text="router")
        self.router_Text = TextBox(self.app, 0, 50)

        self.start_vlan_label = Text(self.app, text="start_vlan")
        self.start_vlan_Text = TextBox(self.app, 0, 50)

        self.start_ip_label = Text(self.app, text="start_ip")
        self.start_ip_Text = TextBox(self.app, 0, 50)

        self.port_count_label = Text(self.app, text="port_count")
        self.port_count_Text = TextBox(self.app, 0, 50)

        self.default_gateway_label = Text(self.app, text="default_gateway")
        self.default_gateway_Text = TextBox(self.app, 0, 50)

        self.clickButton = PushButton(self.app, command=self.on_click_button, text="Config")
        self.result_label = Text(self.app, text="", size=10, color="green")
        self.app.display()
