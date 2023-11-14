import socket

def query_server():
    """
    Query the server via UDP to get server data
    :param obj: The current server object
    :return:
    """
    # server_host_value = obj.server_host
    # server_port_value = obj.server_port
    server_port_value = 7778
    server_host_value = '23.88.115.47'
    print(server_port_value)
    print(server_host_value)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Create a socket connection
        sock.settimeout(5)  # Set a timeout for the socket

        # Construct the UQP query string
        query_string = '\\info\\'
        print(query_string)

        # Send the query to the server
        sock.sendto(query_string.encode(), (server_host_value, int(server_port_value)))

        # Receive and decode the response
        response, _ = sock.recvfrom(2048)
        print(f"Raw Response: {response}")
        print(f"Response Type: {type(response)}")
        response = response.decode("utf-8", errors="replace")
        print(response)

    except Exception as e:
        print("Error querying UT99 server:", str(e))

    finally:
        # Close the socket connection
        sock.close()


if __name__ == '__main__':
    query_server()
