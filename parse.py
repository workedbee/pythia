import json
import locale
import datetime


def get_team_convertor(file_name):
    with open(file_name, 'r') as team_file:
        text = team_file.read()
        return json.loads(text.decode("utf-8"))

def convert_team_name(name, convertor):
    name = name.decode("utf-8")
    if name in convertor:
        name = convertor[name]
    return name

def parse_liga_stavok_html(data):
    locale.setlocale(locale.LC_ALL, 'RUS')

    index = 0
    counter = 0

    team_convertor = get_team_convertor("C:\\Users\\workedbee\\Desktop\\bets\\khl2016\\liga_stavok_teams.json")

    start_sequence = "<h1><nobr><a href = '/Topics/Ice-Hockey'"
    stop_sequence = 'var index = document.URL.indexOf("#");'

    start_sequence_index = data.find(start_sequence)
    stop_sequence_index = data.find(stop_sequence)

    data = data[start_sequence_index: stop_sequence_index]

    games = list()
    while True:
        teams_draft, index = parseData(data, index, '<a href="/Topics/SportEventDetails', '</a>')
        winA, index = parseData(data, index, 'class="addToCartControlLink">', '</a>')
        draw, index = parseData(data, index, 'class="addToCartControlLink">', '</a>')
        winB, index = parseData(data, index, 'class="addToCartControlLink">', '</a>')
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

def parse_sports_ru_html(data, start_game_index):
    locale.setlocale(locale.LC_ALL, 'RUS')

    index = 0
    counter = start_game_index

    start_sequence = '<table class="stat-table" cellpadding="0" cellspacing="0">'
    stop_sequence = '<aside class="aliens aliens_label aliens_margin_vertical_15" data-control="Banners.DFP" data-type="middle"></aside>'

    start_sequence_index = data.find(start_sequence)
    stop_sequence_index = data.find(stop_sequence)

    data = data[start_sequence_index: stop_sequence_index]

    games = list()
    while True:
        date, index = parseData(data, index, '.html">\n', '</a>')
        title, index = parseData(data, index, ' title="', '"')
        teamA, index = parseData(data, index, ' title="', '"')
        otBegIndex = index
        score, index = parseData(data, index, '<b>', '</b>')
        title, index = parseData(data, index, ' title="', '"')
        otEndIndex = index
        teamB, index = parseData(data, index, ' title="', '"')
        if index == -1:
            break

        overtime = findOverTime(data, otBegIndex, otEndIndex)
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

def sportsRuParseFile(inFile, outFile):
    locale.setlocale(locale.LC_ALL, 'RUS')

    with open(inFile, 'r') as rawFile:
        data=rawFile.read().replace('\n', '')

    counter = 0
    index = 0
    games = list()
    while True:
        date, index = parseData(data, index, 'td class="name-td alLeft">', ',')
        title, index = parseData(data, index, ' title="', '"')
        teamA, index = parseData(data, index, ' title="', '"')
        otBegIndex = index
        score, index = parseData(data, index, '<b>', '</b>')
        title, index = parseData(data, index, ' title="', '"')
        otEndIndex = index
        teamB, index = parseData(data, index, ' title="', '"')
        if index == -1:
            break

        overtime = findOverTime(data, otBegIndex, otEndIndex)
        counter = counter + 1

        scores = score.split(':')
        games.append('{' + '"index": "{0}", "date":"{1}", "teamA": "{2}", "teamB": "{3}", "scoreA": "{4}", "scoreB": "{5}", "overtime": "{6}"'.format(
            counter, date, teamA, teamB, scores[0].strip(' '), scores[1].strip(' '), overtime) + '},')

    print '{} games successfully parsed.'.format(len(games))

    with open(outFile, 'w') as jsonFile:
        jsonFile.write('[\n')
        for line in games:
            jsonFile.write(line + '\n')
        jsonFile.write(']')


def parseData(data, index, startSyms, closeSyms):
    if index == -1:
        return '', -1
    
    start = data.find(startSyms, index) + len(startSyms)
    close = data.find(closeSyms, start)
    if start == -1 or close == -1 or start < index or close < index:
        return '', -1
    else:
        return data[start: close-len(data)], close+1

def findOverTime(data, begIndex, endIndex):
    if begIndex == -1 or endIndex == -1:
        return 'false'

    subString = data[begIndex: endIndex]
    if '\x20\xD0\xBE\xD1\x82' in subString or '\xD0\xBE\xD1\x82\x20' in subString or '\x20\xD0\xB1' in subString or '\xD0\xB1\x20' in subString:
        return True
    else:
        return False


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
        time_draft, index = parseData(data, index, '<td class="centerTxt liveeventTime"><span><script>printShortDate(', ')</script></span></td>')
        id_draft, index = parseData(data, index, '<a href="', '" ')
        teams_draft, index = parseData(data, index, 'class="nou2">', '</a>')
        winA, index = parseData(data, index, "><strong>", "</strong></a>")
        draw, index = parseData(data, index, "><strong>", "</strong></a>")
        winB, index = parseData(data, index, "><strong>", "</strong></a>")

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