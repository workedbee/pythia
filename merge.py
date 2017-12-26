import os
import json

directory = '.\\data'
games_directory = '.\\games'


def load_odds():
    files = list()
    for file_name in os.listdir(directory):
        if file_name.startswith("summary_"):
            files.append(os.path.join(directory, file_name))

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
        prob_a = list()
        prob_b = list()
        prob_d = list()
        for odd in odds:
            odd['probA'] = 1./odd['winA'] if odd['winA'] != 0. else 0.0
            prob_a.append("{0:.3f}".format(odd['probA']))
            odd['probB'] = 1./odd['winB'] if odd['winB'] != 0. else 0.0
            prob_b.append("{0:.3f}".format(odd['probB']))
            odd['probDraw'] = 1./odd['draw'] if odd['draw'] != 0. else 0.0
            prob_d.append("{0:.3f}".format(odd['probDraw']))

        date = game["date"].split(' ')[0]
        date = date.replace('-', '_')
        print u"{} {} - {}".format(date, game['teamA'], game['teamB'])

        filename = u"{}_{}_{}_a.txt".format(date, game['teamA'], game['teamB'])
        file_path = os.path.join(games_directory, filename)
        print_to_file(file_path, prob_a)

        filename = u"{}_{}_{}_b.txt".format(date, game['teamA'], game['teamB'])
        file_path = os.path.join(games_directory, filename)
        print_to_file(file_path, prob_b)

        filename = u"{}_{}_{}_d.txt".format(date, game['teamA'], game['teamB'])
        file_path = os.path.join(games_directory, filename)
        print_to_file(file_path, prob_d)

    return games


def print_to_file(file_path, target):
    with open(file_path, 'w') as file:
        content = ''
        for index in range(0, len(target)):
            content += "{} {}\n".format(index, target[index])
        file.write(content)

        # for upshot_type in ['probA', 'probB', 'probDraw']:
        #     min = 1.0
        #     max = 0.0
        #     for odd in odds:
        #         min = odd[upshot_type] if odd[upshot_type] < min else min
        #         max = odd[upshot_type] if odd[upshot_type] > max else max
        #     game[upshot_type] = {}
        #     game[upshot_type]['min'] = min
        #     game[upshot_type]['max'] = max
        #
        # threshold = 0.05
        # if ((module(game['probA']['min'], game['probA']['max']) > threshold) or (module(game['probB']['min'], game['probB']['max']) > threshold)):
        #     print u"{}. {} {} - {}: {} - {}".format(index, game['date'], game['teamA'], game['teamB'], game['probA'], game['probB'])


def module(a, b):
    return (a-b) if a > b else (b-a)


if __name__ == "__main__":
    load_odds()