from copy import deepcopy

from games import load, split_games
from history import load_json, save_data
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
    games = load_json('./data/khl_enriched_games_2018.json')


def prepare():
    team_aliases = load_aliases('./data/team_aliases.json')
    odds = load_json('./data/khl_odds_2018_translated.json')
    games = load_json('./data/khl_games_2018_translated.json')

    featured_data = glue_games_and_odds(games, odds)
    for data in featured_data:
        print data

    save_data(featured_data, './data/khl_enriched_games_2018.json')


def transform_date(date):
    date_time = date.split(' ')
    y_m_d = date_time[0].split('-')
    return '{}.{}.{}'.format(y_m_d[2], y_m_d[1], y_m_d[0])


def translate(items_list, team_aliases):
    for item in items_list:
        translate_team_names(item, team_aliases)


def glue_games_and_odds(games, odds):
    result = []
    for game in games:
        found_odds = find_odds(odds, game['teamA'], game['teamB'], game['date'])
        if len(found_odds) != 1:
            print "Cannot match odd and game result"
            continue
        result_item = deepcopy(game)
        result_item['odds'] = found_odds[0]['odds']
        result.append(result_item)
    return result


def find_odds(odds, teamA, teamB, date):
    result = []
    for odd in odds:
        if odd['teamA'] == teamA \
                and odd['teamB'] == teamB \
                and odd['date'] == date:
            result.append(odd)
    return result


def normalize(values):
    max_value = max(values)
    if max_value == 0.:
        return list
    return [x/max_value for x in values]


if __name__ == "__main__":
    main()