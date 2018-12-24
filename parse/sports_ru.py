import locale

from parse import parse_chunk


def parse_sports_ru_html(data, start_game_index):
    # locale.setlocale(locale.LC_ALL, 'RUS')

    index = 0
    counter = start_game_index

    start_sequence = '<table class="stat-table" cellpadding="0" cellspacing="0">'
    stop_sequence = '</table>'

    start_sequence_index = data.find(start_sequence)
    stop_sequence_index = data.find(stop_sequence, start_sequence_index)

    data = data[start_sequence_index: stop_sequence_index]

    games = list()

    stub, index = parse_chunk(data, index, '<thead>', '</thead>')
    while True:
        stub, index = parse_chunk(data, index, '<td class="name-td alLeft">', '<a')
        date, index = parse_chunk(data, index, '">\n', '<span class')
        title, index = parse_chunk(data, index, ' title="', '"')
        teamA, index = parse_chunk(data, index, ' title="', '"')

        overtime_start_index = index
        score, index = parse_chunk(data, index, '<b>', '</b>')
        title, index = parse_chunk(data, index, ' title="', '"')
        overtime_end_index = index

        teamB, index = parse_chunk(data, index, ' title="', '"')
        if index == -1:
            break

        overtime = find_over_time(data, overtime_start_index, overtime_end_index)
        scores = score.split(':')
        games.append({
            "index": counter,
            "date": date,
            "teamA": teamA.decode("utf-8"),
            "teamB": teamB.decode("utf-8"),
            "scoreA": scores[0].strip(' '),
            "scoreB": scores[1].strip(' '),
            "overtime": overtime
        })
        counter = counter + 1

    return games


def find_over_time(data, beg_index, end_index):
    if beg_index == -1 or end_index == -1:
        return 'false'

    sub_string = data[beg_index: end_index]
    if '\x20\xD0\xBE\xD1\x82' in sub_string \
            or '\xD0\xBE\xD1\x82\x20' in sub_string \
            or '\x20\xD0\xB1' in sub_string \
            or '\xD0\xB1\x20' in sub_string:
        return True
    else:
        return False
