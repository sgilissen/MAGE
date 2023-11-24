import socket
from celery import shared_task
from django.core.cache import cache
from pyq3serverlist import Server as Q3Server
from pyq3serverlist import PyQ3SLError, PyQ3SLTimeoutError


@shared_task
def query_ut99_server(obj):
    """
    Query the server via UDP to get server data
    :param obj: The current server object
    :return:
    """
    server_host_value = obj.server_host
    server_port_value = obj.server_port
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Create a socket connection
        sock.settimeout(1)  # Set a timeout for the socket

        # Construct the UQP query string
        query_string = "\\info\\"

        # Send the query to the server
        # UT99 UDP query uses gameport + 1
        sock.sendto(query_string.encode(), (server_host_value, int(server_port_value) + 1))

        # Receive and decode the response
        response, _ = sock.recvfrom(2048)
        response = response.decode("utf-8", errors="replace")

        # Parse the response and format to dict
        pairs = response.split('\\')[1:]
        result_dict = dict(zip(pairs[::2], pairs[1::2]))
        result_dict['status'] = 'Available'

        # return result_dict
        cache.set(f'ut99-{obj.server_host}', result_dict, timeout=60)

    except Exception as e:
        print(f"Error querying UT99 server {server_host_value}[{server_port_value}]: {str(e)}")
        sock.close()

        result_dict = {
            'status': 'Unreachable',
            'maptitle': 'N/A',
            'mapname': 'N/A',
            'gametype': 'N/A',
            'numplayers': 'N/A',
            'maxplayers': 'N/A'
        }
        cache.set(f'ut99-{obj.server_host}', result_dict, timeout=60)

    finally:
        # Close the socket connection
        sock.close()


@shared_task
def query_q3a_server(obj):
    # Instantiate server object
    server_host_value = obj.server_host
    server_port_value = int(obj.server_port)
    server = Q3Server(server_host_value, server_port_value)

    # Gametype dict
    sv_gametypes = {
        '0': "Deathmatch",
        '1': "1v1 Tournament",
        '2': "1PDM",  # Not used in multiplayer but added for completeness
        '3': "Team Deathmatch",
        '4': "Capture the Flag"
    }

    try:
        # Fetch the server data
        info = server.get_status()

        # Build the dictionary
        result_dict = {
            'status': 'Available',
            'maptitle': info['mapname'],
            'mapname': info['mapname'],
            'gametype': sv_gametypes[info['g_gametype']],
            'numplayers': len(info['players']),
            'maxplayers': info['sv_maxclients'],
        }
        # Save to cache
        cache.set(f'q3a-{obj.server_host}', result_dict, timeout=60)

    except (PyQ3SLTimeoutError, PyQ3SLError) as e:
        print(f"Error querying UT99 server {server_port_value}[{server_port_value}]: {str(e)}")
        # Build the dictionary
        result_dict = {
            'status': 'Unreachable',
            'maptitle': 'N/A',
            'mapname': 'N/A',
            'gametype': 'N/A',
            'numplayers': 'N/A',
            'maxplayers': 'N/A'
        }
        # Save to cache
        cache.set(f'q3a-{obj.server_host}', result_dict, timeout=60)
