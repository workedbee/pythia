import locale

from games import load, split_games


def main():
    locale.setlocale(locale.LC_ALL, 'RUS')

    all_games = load()
    past_games, future_games = split_games(all_games)

    features = list()

    feature_id = 1
    for game in past_games:
        feature_team_a = extract_feature(feature_id, 0)
        feature_team_b = extract_feature(feature_id, 1)

        features.insert(feature_team_a)
        features.insert(feature_team_b)




def extract_feature(id, team_idx):
    return {
        "id": id
    }


if __name__ == "__main__":
    main()