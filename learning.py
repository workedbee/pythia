import locale

from games import load, split_games
from history import load_history_dict

MIN_GAMES_COUNT = 30


def build_csv():
    locale.setlocale(locale.LC_ALL, 'RUS')

    all_games = load()
    past_games, future_games = split_games(all_games)

    features = list()

    feature_id = 1
    for game in past_games:
        feature_team_a = extract_feature(feature_id, 0)
        feature_team_b = extract_feature(feature_id, 1)

        features.append(feature_team_a)
        features.append(feature_team_b)


def extract_feature(id, team_idx):
    return {
        "id": id
    }


def main():
    history_dict = load_history_dict('./data/marathon_khl.json')

    all_games = load()
    past_games, future_games = split_games(all_games)

    game_id_to_graph = dict()
    for key, value in history_dict.items():
        if len(value['odds']) < MIN_GAMES_COUNT:
            continue

        recent_odds = value['odds'][-MIN_GAMES_COUNT:]

        win_a = [x['winA'] for x in recent_odds]
        win_b = [x['winB'] for x in recent_odds]

        game_id_to_graph[key + '_a'] = normalize(win_a)
        game_id_to_graph[key + '_b'] = normalize(win_b)

    k = 0


def normalize(values):
    max_value = max(values)
    if max_value == 0.:
        return list
    return [x/max_value for x in values]


if __name__ == "__main__":
    main()