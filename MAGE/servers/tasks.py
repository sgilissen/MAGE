import socket
from celery import shared_task


@shared_task()
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

        return result_dict

    except Exception as e:
        print(f"Error querying UT99 server: {str(e)}")
        sock.close()

        return {
            'status': 'Unreachable',
            'maptitle': 'N/A',
            'mapname': 'N/A',
            'gametype': 'N/A',
            'numplayers': 'N/A',
            'maxplayers': 'N/A'
        }

    finally:
        # Close the socket connection
        sock.close()