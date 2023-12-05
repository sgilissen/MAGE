import socket


def query_ut2k4_server():
    # Instantiate server object
    server_host_value = "80.4.151.145"
    server_port_value = 7777
    # server_host_value = 'gameserver.noctis.info'
    # server_port_value = 8778

    # Query types:
    # 0x01: Basic info
    # 0x01: Server info
    # 0x02: Player info
    # 0x03: Server info + player info
    query_types = [0x02]

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
