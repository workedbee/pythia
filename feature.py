from history import load_json, save_data


def main():
    games = load_json('./data/khl_enriched_games_2018.json')
    results = []
    features = []

    for game in games:
        odds_count = len(game['odds'])
        if odds_count == 0:
            print u'Game without odd {}: {} - {} '.format(game['date'], game['teamA'], game['teamB'])
            continue
        last_odd = game['odds'][odds_count-1]

        features.append([last_odd['winA']])
        features.append([last_odd['winB']])
        results.append(team_a_win_game(game))
        results.append(team_b_win_game(game))

    save_data({'features': features, 'results': results}, './data/khl_features_2018.json')


def team_a_win_game(game):
    team_a_win = not game['overtime'] and (game['scoreA'] > game['scoreB'])
    return 1 if team_a_win else 0


def team_b_win_game(game):
    team_b_win = not game['overtime'] and (game['scoreA'] < game['scoreB'])
    return 1 if team_b_win else 0

if __name__ == "__main__":
    main()