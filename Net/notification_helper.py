import requests


def notify_switch(switch):
    try:
        requests.post('https://monitoring.frox.ir/switch', data={'switch': switch})
    except:
        pass


def notify_port(port, miner):
    try:
        requests.post('https://monitoring.frox.ir/port', data={'port': port, "miner": miner})
    except:
        pass


def notify_miner(miner):
    try:
        requests.post('https://monitoring.frox.ir/miner', data={'miner': miner})
    except:
        pass
