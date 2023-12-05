import socket
import struct
import re


def query_ut2k4_server():
    # Instantiate server object
    # server_host_value = "217.79.181.250"
    # server_port_value = 7777
    server_host_value = 'gameserver.noctis.info'
    server_port_value = 8778

    # Query types:
    # 0x01: Basic info
    # 0x01: Server info
    # 0x02: Player info
    # 0x03: Server info + player info
    # Make sure to do player info BEFORE anything else
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
                fields = struct.unpack(f'!{len(response)}s', response)[0].split(b'\x00')
                result_dict = {
                    "servername": fields[15].decode('utf-8', 'ignore').strip(control_chars),
                    "maptitle": fields[16].decode('utf-8', 'ignore').strip(control_chars).lower(),
                    "mapname": fields[16].decode('utf-8', 'ignore').strip(control_chars).lower(),
                    "gametype": fields[17].decode('utf-8', 'ignore').strip(control_chars)
                }
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

                    # RegEx to clean name
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

        # return result_dict
        # cache.set(f'ut99server-{obj.server_host}', result_dict, timeout=polling_timeout)
        print(combined_result)

    except Exception as e:
        print(f"Error querying UT2k4 server {server_host_value}[{server_port_value}]: {str(e)}")
        sock.close()

        result_dict = {
            'status': 'Unreachable',
            'maptitle': 'N/A',
            'mapname': 'N/A',
            'gametype': 'N/A',
            'numplayers': 'N/A',
            'maxplayers': 'N/A'
        }
        # cache.set(f'ut99server-{obj.server_host}', result_dict, timeout=polling_timeout)
        # print(result_dict)

    finally:
        # Close the socket connection
        sock.close()


if __name__ == "__main__":
    query_ut2k4_server()
