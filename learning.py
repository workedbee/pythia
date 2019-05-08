from games import load, split_games
from history import load_history_dict
from utils import load_aliases, translate_team_names

MIN_GAMES_COUNT = 30


def build_csv():
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
    odds = load_history_dict('./data/marathon_khl.json').values()

    all_games = load()
    games, future_games = split_games(all_games)

    team_aliases = load_aliases('./data/team_aliases.json')

    translate(games, odds, team_aliases)
    #glue_games_and_odds(games, odds)


def translate(games, odds, team_aliases):
    for game in games:
        translate_team_names(game, team_aliases)
    for odd in odds:
        translate_team_names(odd, team_aliases)


def glue_games_and_odds(games, odds):
    for game in games:
        odd = find_odd(odds, game['teamA'], game['teamB'], game['date'])
        game['odds'] = odd
    return


def find_odd(odds, teamA, teamB, date):
    for odd in odds:
        if odd['teamA'] == teamA and odd['teamB'] == teamB:
            return odd
    return None


def normalize(values):
    max_value = max(values)
    if max_value == 0.:
        return list
    return [x/max_value for x in values]


if __name__ == "__main__":
    main()