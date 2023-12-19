import socket
from celery import shared_task
from celery.utils.log import get_task_logger
from channels.layers import get_channel_layer
from django.core.cache import cache
from pyq3serverlist import Server as Q3Server
from pyq3serverlist import PyQ3SLError, PyQ3SLTimeoutError
import re
import struct

# Set up logging
logger = get_task_logger(__name__)

# Polling timeout. Maybe we can set this up in a setting?
polling_timeout = 60


def wsnotify_serverdata(sender, result, **kwargs):
    # Notify WebSocket consumers
    ...


@shared_task
def query_ut99_server(obj):
    """
    Query the server via UDP to get server data
    :param obj: The current server object
    :return:
    """
    server_host_value = obj.server_host
    server_port_value = obj.server_port
    server_pk = obj.pk
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
        result_dict['status_verbose'] = 'Available'
        result_dict['status'] = 'server_online'

        # return result_dict
        cache.set(f'gameserver-{obj.pk}', result_dict, timeout=polling_timeout)

    except Exception as e:
        logger.exception(f"Error querying UT99 server {server_host_value}[{server_port_value}]: {str(e)}")
        sock.close()

        result_dict = {
            'status_verbose': 'Unreachable',
            'status': 'server_offline',
            'maptitle': 'N/A',
            'mapname': 'N/A',
            'gametype': 'N/A',
            'numplayers': 'N/A',
            'maxplayers': 'N/A'
        }
        cache.set(f'gameserver-{obj.pk}', result_dict, timeout=polling_timeout)

    finally:
        # Close the socket connection
        sock.close()


@shared_task
def query_q3a_server(obj):
    # Instantiate server object
    server_host_value = obj.server_host
    server_port_value = int(obj.server_port)
    server_pk = obj.pk
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
            'status_verbose': 'Available',
            'status': 'server_online',
            'maptitle': info['mapname'],
            'mapname': info['mapname'],
            'gametype': sv_gametypes[info['g_gametype']],
            'numplayers': len(info['players']),
            'maxplayers': info['sv_maxclients'],
        }
        # Save to cache
        cache.set(f'gameserver-{obj.pk}', result_dict, timeout=60)

    except (PyQ3SLTimeoutError, PyQ3SLError) as e:
        logger.exception(f"Error querying Q3A server {server_port_value}[{server_port_value}]: {str(e)}")
        # Build the dictionary
        result_dict = {
            'status_verbose': 'Unreachable',
            'status': 'server_offline',
            'maptitle': 'N/A',
            'mapname': 'N/A',
            'gametype': 'N/A',
            'numplayers': 'N/A',
            'maxplayers': 'N/A'
        }
        # Save to cache
        cache.set(f'gameserver-{obj.pk}', result_dict, timeout=60)


@shared_task
def query_ut2k4_server(obj):
    """
    Query an Unreal Tournament 2004 server via UDP and return a dictionary with the results
    Code by sgilissen (NoctisBE), with special thanks to CVSoft and Dark1.
    :param obj: Django query object
    :return: dictionary
    """
    server_host_value = obj.server_host
    server_port_value = int(obj.server_port)
    server_pk = obj.pk

    # Query types:
    # 0x01: Basic info
    # 0x01: Server info
    # 0x02: Player info
    # 0x03: Server info + player info
    # Make sure to query the player info BEFORE anything else. For some reason the data gets garbled otherwise...
    query_types = [0x02, 0x00, 0x01]

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Create a socket connection
        sock.settimeout(1)  # Set a timeout for the socket

        # Create a new dict for the combined result
        combined_result = {}

        # Construct the UQP queries in a for-loop
        for query_type in query_types:
            query = bytearray([0x78, 0, 0, 0, query_type])

            # Send the query to the server
            # UT2k4 UDP query uses gameport + 1
            sock.sendto(query, (server_host_value, int(server_port_value) + 1))

            # Initialize an empty dict for the current query
            result_dict = {}
            # Receive and decode the response
            response, _ = sock.recvfrom(2048)

            # Iterate over the fields and create key-value pairs, strip control characters

            # I hate doing it this way. Bit hacky. Maybe check if there's a better way later?
            control_chars = ('\x00\x03\x05\x08\x0b\x0c\r\x11\x12\x02\x0e\n\t\x1e\x16'
                             '\x06\x0f\x10\x14\x13\x1b\x80\x01\x0b\x1b\x1a\x19\x1d')
            if query_type == 0x00:
                # Unpack all the fields we know, place it in the dict
                fields = struct.unpack(f'!{len(response)}s', response)[0].split(b'\x00')
                result_dict['servername'] = fields[15].decode('utf-8', 'ignore').strip(control_chars),
                result_dict['maptitle'] = fields[16].decode('utf-8', 'ignore').strip(control_chars)
                result_dict['mapname'] = fields[16].decode('utf-8', 'ignore').strip(control_chars).lower()
                result_dict['gametype'] = fields[17].decode('utf-8', 'ignore').strip(control_chars)

                # Parse the residual data, starting from the gametype as this is the last "readable" info in the packet
                gametype_start = response.find(fields[17])
                gametype_end = gametype_start + len(fields[17])
                res_data = response[gametype_end:]

                # Save to results dictionary we created above with the other data
                result_dict['maxplayers'] = int.from_bytes(res_data[5:9], byteorder='little')
                result_dict['ping'] = int.from_bytes(res_data[9:13], byteorder='little')
                result_dict['flags'] = int.from_bytes(res_data[13:17], byteorder='little')
                result_dict['skill'] = res_data[17]

            elif query_type == 0x01:
                fields = struct.unpack(f'!{len(response)}s', response)[0].split(b'\x00')
                for i in range(3, len(fields) - 1, 2):
                    key = fields[i].decode('utf-8', 'ignore').strip(control_chars)
                    value = fields[i + 1].decode('utf-8', 'ignore').strip(control_chars)
                    result_dict[key] = value

            elif query_type == 0x02:
                players = []

                # Remove the first 5 bytes
                data = response[5:]

                # Set index
                index = 0
                while index < len(data):
                    name_idx_end = data[index + 4:].find(b'\x00')
                    player_name = data[index + 4: index + 4 + name_idx_end].decode('utf-8', errors='ignore')

                    # RegEx to clean the player name
                    player_name = re.sub("\x1b...", "", player_name)
                    player_name = re.sub("[\x00-\x1f]", "", player_name)

                    # If we get teams, break so we don't add these to the player list
                    if player_name == 'Red Team Score':
                        break

                    players.append(player_name)

                    # Move the index to the next entry start
                    index += name_idx_end + 9

                # Remove empty entries
                players = list(filter(None, players))
                result_dict['numplayers'] = len(players)
                result_dict['player_list'] = players

            elif query_type == 0x03:
                fields = struct.unpack(f'!{len(response)}s', response)[0].split(b'\x00')
                for i in range(3, len(fields) - 1, 2):
                    key = fields[i].decode('utf-8', 'ignore').strip(control_chars)
                    value = fields[i + 1].decode('utf-8', 'ignore').strip(control_chars)
                    result_dict[key] = value

            combined_result.update(result_dict)
            combined_result['status_verbose'] = "Available"
            combined_result['status'] = "server_online"

        # return result_dict
        cache.set(f'gameserver-{obj.pk}', combined_result, timeout=polling_timeout)

    except Exception as e:
        logger.exception(f"Error querying UT2k4 server {server_host_value}[{server_port_value}]: {str(e)}")
        sock.close()

        result_dict = {
            'status_verbose': 'Unreachable',
            'status': 'server_offline',
            'maptitle': 'N/A',
            'mapname': 'N/A',
            'gametype': 'N/A',
            'numplayers': 'N/A',
            'maxplayers': 'N/A'
        }
        cache.set(f'gameserver-{obj.pk}', result_dict, timeout=polling_timeout)

    finally:
        # Close the socket connection
        sock.close()
