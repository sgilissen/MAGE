import socket
import struct


def parseString(pos, data):
    i = pos + 1
    res = ""
    while True:
        if data[i] == 0: #end of the string
            break
        if data[i] == 0x1b: #byte color flag then escape RGB triplet
            i += 4
        res += chr(data[i])
        i += 1
    return res, i+1

def parseInt(pos, data):
    return int(data[pos]), pos + 4

def query_ut2k4_server():
    # Instantiate server object
    #server_host_value = obj.server_host
    #server_port_value = int(obj.server_port)
    server_host_value = 'gameserver.noctis.info'
    server_port_value = 8778


    # Query types:
    # 0x01: Basic info
    # 0x01: Server info
    # 0x02: Player info
    # 0x03: Server info + player info
    query_types = [0x00, 0x01, 0x02, 0x03]

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Create a socket connection
        sock.settimeout(1)  # Set a timeout for the socket

        # Create a new dict for the combined result
        combined_result = {}

        # Construct the UQP queries in a for-loop
        for query_type in query_types:
            query = bytearray([0x80, 0, 0, 0, query_type])

            # Set initial position in binary data
            pos = 0

            # Send the query to the server
            # UT2k4 UDP query uses gameport + 1
            sock.sendto(query, (server_host_value, int(server_port_value) + 1))

            # Initialize an empty dict for the current query
            result_dict = {}
            # Receive and decode the response
            response, _ = sock.recvfrom(2048)
            # response = response.decode("utf-8", errors="replace")
            # response = response[5:]
            # print(f"response {query_type} ----")
            # print(response)

            # Unpack the data using the null character as a delimiter


            # fields = struct.unpack('=II', response[:8])[0].split(b'\x00')
            #print(fields)
            # Parse the response and format to dict
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
                print(response)
                players = []

                # Find the start of each player entry
                start_idx = response.find(b'\x02')

                if start_idx != -1 and start_idx + 1 < len(response) and response[start_idx + 1] == 0x00:
                    result_dict['players_list'] = players
                    result_dict['numplayers'] = len(players)

                else:
                    while start_idx != -1:
                        # Check if there's enough data for a complete player entry
                        if start_idx + 8 < len(response):
                            # Extract player data
                            player_data = response[start_idx:start_idx + 8]

                            # Parse ping, score, stats id, team, and player name
                            ping = player_data[1] >> 4
                            score = player_data[1] & 0x0F
                            stats_team = int.from_bytes(player_data[2:4], byteorder='little')
                            team = (stats_team >> 30) & 0x01
                            stats_id = stats_team & 0x3FFFFFFF

                            print("----")
                            print(player_data)
                            print("====")

                            # Extract player name until null terminator '\x00' is encountered
                            name_end_idx = player_data.find(b'\x00', 5)
                            if name_end_idx != -1:
                                player_name = player_data[5:name_end_idx].decode('utf-8')
                            else:
                                player_name = ''


                            # Append player information to the list
                            players.append({
                                'ping': ping,
                                'score': score,
                                'team': 'Red' if team == 1 else 'Blue',
                                'stats_id': stats_id,
                                'name': player_name
                            })

                            # Find the start of the next player entry
                            start_idx = response.find(b'\x02', start_idx + 1)
                        else:
                            break

                    result_dict['players_list'] = players
                    result_dict['numplayers'] = len(players)

            elif query_type == 0x03:
                fields = struct.unpack(f'!{len(response)}s', response)[0].split(b'\x00')
                for i in range(3, len(fields) - 1, 2):
                    key = fields[i].decode('utf-8', 'ignore').strip(control_chars)
                    value = fields[i + 1].decode('utf-8', 'ignore').strip(control_chars)
                    result_dict[key] = value

            # print(f"----------- fields {query_type} -----------")
            # print(result_dict)

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
