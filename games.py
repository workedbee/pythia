from http import load_html_page
from parse.sports_ru import parse_sports_ru_html

def load():
    #khl_2016_season_id = '5735'
    #khl_2017_season_id = '6449'
    khl_2018_season_id = '6928'
    #khl_2016_season_id = '5736'
    #khl_2016_season_id = '5547'

    game_index = 0
    games = list()
    #months = [8, 9, 10, 11, 12, 1, 2]
    months = [8, 9, 10, 11, 12, 1, 2, 3]
    months = [9]
    #months = [10, 11, 12, 1, 2, 3, 4]
    try:
        for month in months:
            parameters = {
                "s": khl_2018_season_id,
                "m": str(month)
            }
            data = load_html_page("https://www.sports.ru/khl/calendar/", parameters)
            games_portion = parse_sports_ru_html(data, game_index)
            games.extend(games_portion)
            game_index += len(games_portion)

    except Exception as e:
        print "KeyError Encounter - missing JSON object from the response : {}".format(e)
        print "Response returned from the server"

    return games


def split_games(games):
    last_games = list()
    future_games = list()
    for game in games:
        if '-' in game["scoreA"]:
            future_games.append(game)
        else:
            last_games.append(game)

    return last_games, future_games
