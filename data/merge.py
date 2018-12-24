import os
import json

directory = 'C:\\Users\\WORKEDBEE\\Desktop\\amazon\\bak'
start_file = ''


def main():
    files = list()
    for file in os.listdir(directory):
        if file.startswith("summary_"):
            files.append(os.path.join(directory, file))

    game_by_id = dict()
    for filename in files:
        with open(filename, 'r') as data_file:
            data = data_file.read()
            json_games = json.loads(data)

            for game in json_games:
                if game['id'] in game_by_id:
                    game_to_append = game_by_id[game['id']]
                    game_to_append['odds'] = list(game_to_append['odds'] + game['odds'])
                else:
                    game_by_id[game['id']] = game

    games = game_by_id.values()
    index = 0
    games = sorted(games, key=lambda game: game['date'])

    for game in games:
        index += 1
        odds = game['odds']
        odds = sorted(odds, key = lambda odd: odd['time'])
        for odd in odds:
            odd['probA'] = 1./odd['winA'] if odd['winA'] != 0. else 0.0
            odd['probB'] = 1./odd['winB'] if odd['winB'] != 0. else 0.0
            odd['probDraw'] = 1./odd['draw'] if odd['draw'] != 0. else 0.0

        for upshot_type in ['probA', 'probB', 'probDraw']:
            min = 1.0
            max = 0.0
            for odd in odds:
                min = odd[upshot_type] if odd[upshot_type] < min else min
                max = odd[upshot_type] if odd[upshot_type] > max else max
            game[upshot_type] = {}
            game[upshot_type]['min'] = min
            game[upshot_type]['max'] = max

        threshold = 0.05
        if ((module(game['probA']['min'], game['probA']['max']) > threshold) or (module(game['probB']['min'], game['probB']['max']) > threshold)):
            print u"{}. {} {} - {}: {} - {}".format(index, game['date'], game['teamA'], game['teamB'], game['probA'], game['probB'])


def module(a, b):
    return (a-b) if a > b else (b-a)

if __name__ == "__main__":
    main()