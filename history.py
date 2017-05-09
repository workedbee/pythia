import json
import locale
import datetime
from os.path import join, isfile
from os import path, listdir
from http import load_html_page
from parse import parse_leon_bet_html


script_directory = path.dirname(path.abspath(__file__))


def main():
    locale.setlocale(locale.LC_ALL, 'RUS')
    get_leon_bets_history()


def get_path_in_script_dir(filename):
    return join(script_directory, filename)


def save_history_dict(history_dict, filename):
    with open(filename, 'w') as data_file:
        json.dump(history_dict.values(), data_file)


def load_json(filename):
    with open(filename) as data_file:
        result = json.load(data_file)

    return result


def load_history_dict(filename):
    history = load_json(filename)

    history_dict = dict()
    for game in history:
        history_dict[game["id"]] = game

    return history_dict


def add_odds_to_history(games, history_dict):
    for game in games:
        if game["id"] in history_dict:
            game_with_odds = history_dict[game["id"]]
            game_with_odds["odds"].extend(game["odds"])
        else:
            history_dict[game["id"]] = game


def get_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def print_history(history):
    for game in history:
        text = u'{}: {} - {}'.format(game['date'], game['teamA'], game['teamB'])
        print text.encode('utf-8')
        for odd in game["odds"]:
            print '\t{}: {:0.2f} / {:0.2f} / {:0.2f}'.format(odd['time'], odd['winA'], odd['draw'], odd['winB'])


def get_leon_bets_history():
    configuration = load_json(get_path_in_script_dir('configuration.json'))

    filename_to_update = get_path_in_script_dir("summary.json")
    history_dict = load_history_dict(filename_to_update)

    for competition in configuration:
        data = load_html_page(competition["url"], {})
        current_datetime = get_time()
        games = parse_leon_bet_html(current_datetime, data)
        add_odds_to_history(games, history_dict)

    print_history(history_dict.values())

    save_history_dict(history_dict, filename_to_update)


def load_from_files():
    files_path = join(script_directory, 'load')
    files = [f for f in listdir(files_path) if isfile(join(files_path, f))]

    all_games = list()
    for file_name in files:
        full_name = join(files_path, file_name)
        with open(full_name, 'r') as file_descriptor:
            content = file_descriptor.read()
            time = parse_file_name(file_name)
            games = parse_leon_bet_html(time, content)
            all_games.extend(games)


def parse_file_name(file_name):
    content = file_name.replace('Basketball_1800_', '')
    content = content.replace('.txt', '')
    parts = content.split('_')
    return parts[0] + ' ' + parts[1].replace('-', ':')


if __name__ == "__main__":
    main()