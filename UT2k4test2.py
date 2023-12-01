import socket

def query_ut2004_server(server_ip, server_port):
    # Create a UDP socket
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        # Craft the query packet
        packet = b'\xFE\xFD\x09\x10\x20\x30\x40\xFF\xFF\xFF\x01\xFF\xFF\xFF\x01'

        # Send the packet to the server
        udp_socket.sendto(packet, (server_ip, server_port))

        # Receive the response
        response, _ = udp_socket.recvfrom(4096)

        # Parse the response
        server_info = parse_ut2004_response(response)

        return server_info

    except Exception as e:
        print(f"Error querying UT2004 server: {e}")

    finally:
        # Close the socket
        udp_socket.close()

def parse_ut2004_response(response):
    # Extract relevant information from the response
    # Customize this function based on the actual response format
    # The GameSpy Query protocol documentation can help with this: https://web.archive.org/web/20170801135226/http://hlmaster.com:80/hlmaster/docs/server_query.html
    server_info = {}
    # ...parse the response and populate server_info...

    return server_info

# Example usage
server_ip = 'your_server_ip'
server_port = 7777  # Default UT2004 server port
result = query_ut2004_server(server_ip, server_port)

if result:
    print("Server Info:")
    for key, value in result.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    print(query_ut2004_server("gameserver.noctis.info", 10777))
