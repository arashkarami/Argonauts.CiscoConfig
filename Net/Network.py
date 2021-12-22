def mac_normalize(mac_address: str):
    return mac_address.upper().replace(":", "").replace(",", "").replace(".", "")


def port_name(host, port):
    port = port[0] + port.split("/")[-1]
    name = "{}-{}".format(host, port)
    return name
