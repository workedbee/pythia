from enrich import hyperbole
from graph_detector import detect_graph
from history import load_json, save_data

MIN_ODDS_COUNT = 30
ODDS_ROW_END_NOT_TAKEN = 0


def main():
    games = load_json('./data/khl_enriched_games_2018.json')
    results = []
    features = []
    graphs = []

    for game in games:
        odds_count = len(game['odds'])
        if odds_count < MIN_ODDS_COUNT:
            print u'Game has not enough odds ({}) {}: {} - {} '.format(odds_count, game['date'], game['teamA'], game['teamB'])
            continue

        graph_a = build_graph(game, True)
        graph_b = build_graph(game, False)
        graphs.append(graph_a)
        graphs.append(graph_b)

        team_a_feature = build_feature(game, graph_a, True)
        team_b_feature = build_feature(game, graph_b, False)
        features.append(team_a_feature)
        features.append(team_b_feature)

        results.append(team_a_win_game(game))
        results.append(team_b_win_game(game))

    save_data({'features': features, 'results': results, 'graphs': graphs}, './data/khl_features_2018.json')
    print 'Saved {} features'.format(len(features))


def build_graph(game, team_a):
    team_win_name = 'winA' if team_a else 'winB'

    recent_odds = game['odds'][-MIN_ODDS_COUNT:-ODDS_ROW_END_NOT_TAKEN] if ODDS_ROW_END_NOT_TAKEN != 0 else game['odds'][-MIN_ODDS_COUNT:]
    graph = [hyperbole(x[team_win_name]) for x in recent_odds]
    return graph


def build_feature(game, graph, team_a):
    team_win_name = 'winA' if team_a else 'winB'

    odds_count = len(game['odds'])
    first_odd = game['odds'][0]
    last_odd = game['odds'][odds_count - 1]

    graph_type = detect_graph(graph)

    last_value = hyperbole(last_odd[team_win_name])
    first_value = hyperbole(first_odd[team_win_name])

    feature = list()
    # 1. last odd coefficient
    feature.append(last_odd[team_win_name])
    # # 2. is graph increasing
    # feature.append(1 if graph_type == GRAPH_TYPE_INCREASING else 0)
    # # 3. is graph decreasing
    # feature.append(1 if graph_type == GRAPH_TYPE_DECREASING else 0)
    # # 4. is graph grows up and falls down
    # feature.append(1 if graph_type == GRAPH_TYPE_UP_AND_DOWN else 0)
    # # 5. is graph falls down and grows up
    # feature.append(1 if graph_type == GRAPH_TYPE_DOWN_AND_UP else 0)
    # # 6. max/first odd ratio
    # max_odd = max(graph)
    # feature.append(last_value-first_value)
    # # 7. min/first odd ratio
    # min_odd = min(graph)
    # feature.append(first_value-min_odd)

    return feature


def team_a_win_game(game):
    team_a_win = not game['overtime'] and (game['scoreA'] > game['scoreB'])
    return 1 if team_a_win else 0


def team_b_win_game(game):
    team_b_win = not game['overtime'] and (game['scoreA'] < game['scoreB'])
    return 1 if team_b_win else 0


if __name__ == "__main__":
    main()