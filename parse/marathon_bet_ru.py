from parse import parse_chunk


def parse_bet_html(current_datetime, data):
    whole_start_sequence = '<td data-category-events-link-container='
    whole_stop_sequence = '<div id="body_footer" ></div>'

    whole_start_index = data.find(whole_start_sequence)
    whole_stop_index = data.find(whole_stop_sequence)

    data = data[whole_start_index: whole_stop_index]

    games = list()

    index = 0
    while True:
        game_id, index = parse_chunk(data, index, 'data-event-treeId="', '"')

        stub, index = parse_chunk(data, index, 'member-name nowrap', 'data-ellipsis=')
        team_a, index = parse_chunk(data, index, '<span>', '</span>')

        stub, index = parse_chunk(data, index, 'member-name nowrap', 'data-ellipsis=')
        team_b, index = parse_chunk(data, index, '<span>', '</span>')

        stub, index = parse_chunk(data, index, 'data-selection-key="', '@Result.1')
        win_a, index = parse_chunk(data, index, ">", "</span>")

        stub, index = parse_chunk(data, index, 'data-selection-key="', 'Result.draw')
        draw, index = parse_chunk(data, index, ">", "</span>")

        stub, index = parse_chunk(data, index, 'data-selection-key="', '@Result.3')
        win_b, index = parse_chunk(data, index, ">", "</span>")

        if index == -1:
            break

        games.append({
            "id": game_id,
            "date": current_datetime,
            "teamA": team_a.decode("utf-8"),
            "teamB": team_b.decode("utf-8"),
            "odds": [{
                "time": current_datetime,
                "winA": float(win_a.replace('\r\n', '').replace(' ', '')),
                "draw": float(draw.replace('\r\n', '').replace(' ', '')),
                "winB": float(win_b.replace('\r\n', '').replace(' ', ''))
            }]
        })

    return games