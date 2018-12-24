import json
import locale
import datetime


def get_team_converter(file_name):
    with open(file_name, 'r') as team_file:
        text = team_file.read()
        return json.loads(text.decode("utf-8"))


def convert_team_name(name, converter):
    name = name.decode("utf-8")
    if name in converter:
        name = converter[name]
    return name


def parse_liga_stavok_html(data):
    locale.setlocale(locale.LC_ALL, 'RUS')

    index = 0
    counter = 0

    team_convertor = get_team_converter("C:\\Users\\workedbee\\Desktop\\bets\\khl2016\\liga_stavok_teams.json")

    start_sequence = "<h1><nobr><a href = '/Topics/Ice-Hockey'"
    stop_sequence = 'var index = document.URL.indexOf("#");'

    start_sequence_index = data.find(start_sequence)
    stop_sequence_index = data.find(stop_sequence)

    data = data[start_sequence_index: stop_sequence_index]

    games = list()
    while True:
        teams_draft, index = parse_chunk(data, index, '<a href="/Topics/SportEventDetails', '</a>')
        winA, index = parse_chunk(data, index, 'class="addToCartControlLink">', '</a>')
        draw, index = parse_chunk(data, index, 'class="addToCartControlLink">', '</a>')
        winB, index = parse_chunk(data, index, 'class="addToCartControlLink">', '</a>')
        if index == -1:
            break
        result, teamA, teamB = parse_team_draft(teams_draft)
        if not result:
            continue

        games.append({
            "index": counter,
            "teamA": convert_team_name(teamA, team_convertor),
            "teamB": convert_team_name(teamA, team_convertor),
            "winA": float(winA.replace(',', '.')),
            "draw": float(draw.replace(',', '.')),
            "winB": float(winB.replace(',', '.'))
        })
        counter = counter + 1

    return games

def parse_team_draft(draft):
    parts = draft.split('>')
    if len(parts) < 2:
        return False, '', ''
    parts = parts[1].split(' - ')
    if len(parts) < 2:
        return False, '', ''
    return True, parts[0].strip(), parts[1].strip()


def parse_chunk(data, index, startSyms, closeSyms):
    if index == -1:
        return '', -1
    
    start = data.find(startSyms, index) + len(startSyms)
    close = data.find(closeSyms, start)
    if start == -1 or close == -1 or start < index or close < index:
        return '', -1
    else:
        return data[start: close-len(data)], close+1


def parse_leon_team_draft(draft):
    draft = draft.replace('\r\n', '')

    parts = draft.split(' - ')
    if len(parts) < 2:
        return False, '', ''
    return True, parts[0].strip(), parts[1].strip()


def parse_leon_id_draft(draft):
    return draft.replace('https://www.leon.ru/betevent/', '')


def parse_leon_date_draft(draft):
    time_ms = long(draft)
    return str(datetime.datetime.fromtimestamp(time_ms/1000.0))

def parse_leon_bet_html(current_datetime, data):
    locale.setlocale(locale.LC_ALL, 'RUS')

    whole_start_sequence = 'table border="0" cellspacing="1"'
    whole_stop_sequence = '<div class="betoffer-hint text-wrapper sport-desc">'

    whole_start_index = data.find(whole_start_sequence)
    whole_stop_index = data.find(whole_stop_sequence)

    data = data[whole_start_index: whole_stop_index]

    games = list()

    index = 0
    while True:
        time_draft, index = parse_chunk(data, index, '<td class="centerTxt liveeventTime"><span><script>printShortDate(', ')</script></span></td>')
        id_draft, index = parse_chunk(data, index, '<a href="', '" ')
        teams_draft, index = parse_chunk(data, index, 'class="nou2">', '</a>')
        winA, index = parse_chunk(data, index, "><strong>", "</strong></a>")
        draw, index = parse_chunk(data, index, "><strong>", "</strong></a>")
        winB, index = parse_chunk(data, index, "><strong>", "</strong></a>")

        if index == -1:
            break
        result, teamA, teamB = parse_leon_team_draft(teams_draft)
        if not result:
            continue

        id = parse_leon_id_draft(id_draft)

        date = parse_leon_date_draft(time_draft)

        games.append({
            "id": id,
            "date": date,
            "teamA": teamA.decode("utf-8"),
            "teamB": teamB.decode("utf-8"),
            "odds": [{
                "time": current_datetime,
                "winA": float(winA.replace('\r\n', '').replace(' ', '')),
                "draw": float(draw.replace('\r\n', '').replace(' ', '')),
                "winB": float(winB.replace('\r\n', '').replace(' ', ''))
            }]
        })

    return games