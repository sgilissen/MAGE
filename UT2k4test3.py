def parse_players(query_result):
    players = []
    start_idx = query_result.find(b'\x02')

    while start_idx != -1:
        end_idx = query_result.find(b'\x02', start_idx + 1)

        if end_idx == -1:
            break  # The last player entry

        player_data = query_result[start_idx + 1:end_idx].decode('utf-8', 'ignore')

        # Assuming the player name is terminated by null character
        null_idx = player_data.find('\x00')
        player_name = player_data[:null_idx]

        # You may need to adjust the following based on the actual data structure
        player_info = {
            'name': player_name,
            'data': player_data[null_idx + 1:]  # Assuming the null character separates the name and the rest of the data
        }

        players.append(player_info)

        start_idx = end_idx

    return players

# Example usage:
query_result = b'\x80\x00\x00\x00\x02\x15\x00\x00\x00\x12SUPER!_Mario (DE)\x00|\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00@\x14\x00\x00\x00\x16MajorCatastrophe (US)\x00d\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00@\x12\x00\x00\x00\x08JP (NL)\x00\x18\x00\x00\x00\x13\x00\x00\x00\x00\x00\x00 \x0e\x00\x00\x00\x13Grim_Fandango (UK)\x00\x1c\x00\x00\x00\x12\x00\x00\x00\x00\x00\x00@\x0b\x00\x00\x00\x0fBallerina (DE)\x00\x18\x00\x00\x00\x0e\x00\x00\x00\x00\x00\x00 \n\x00\x00\x00\tICH (DE)\x00 \x00\x00\x003\x00\x00\x00\x00\x00\x00@\x08\x00\x00\x00\x13WorldIsMental (IN)\x00\xfc\x00\x00\x00M\x00\x00\x00\x00\x00\x00 \x06\x00\x00\x00\x13<TOL>Glassman (US)\x00\\\x00\x00\x00\x11\x00\x00\x00\x00\x00\x00@\x03\x00\x00\x00\x14(..<[TORO]>..) (MX)\x00\x80\x00\x00\x00Y\x00\x00\x00\x00\x00\x00@\x02\x00\x00\x00\rbiocell (FI)\x004\x00\x00\x00 \x00\x00\x00\x00\x00\x00 \x01\x00\x00\x00\rChangal (CZ)\x00(\x00\x00\x00P\x00\x00\x00\x00\x00\x00'
players_result = parse_players(query_result)

# Print the result
for player in players_result:
    print(player)