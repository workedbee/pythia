import json
import locale
import os
from os import path

import numpy as np
from sklearn import linear_model

import analyze
from analyze import logColumns
from enrich import GameResult
from enrich import enrich_odds
from games import load, split_games
from http import load_html_page
from merge import print_list_to_file
from parse.marathon_bet_ru import parse_bet_html
from parse.parse import parse_liga_stavok_html
from utils import load_aliases

work_directory = path.dirname(path.abspath(__file__))
games_directory = path.join(work_directory, "games")


def print_team_statistic(team_statistic):
    index = 0
    for ts in team_statistic:
        index += 1
        print u"{}. {} - {}".format(index, ts['name'], float(ts['score'])/len(ts['games']))


def main():
    locale.setlocale(locale.LC_ALL, 'RUS')

    all_games = load()
    past_games, future_games = split_games(all_games)

    games = past_games
    odds = get_marathon_odds()

    k = 0
    games = enrich_games(games)
    teams = extract_teams(games)

    statistics_by_team = generate_statistics_by_team(teams, games)
    enrich_by_series(statistics_by_team, games)

    all_teams_statistics = sorted(statistics_by_team.values(), key=lambda x: x["score"], reverse=True)
    print_team_statistic(all_teams_statistics)

    odds = load_odds()
    aliases = load_aliases(path.join(work_directory, 'data\\team_aliases.json'))

    investigate_suspicious2(games, odds, aliases)

    series = list()
    for team_statistics in all_teams_statistics:
        [series.append(seria) for seria in team_statistics["series"]]

    incomplete_series = list()
    for team_statistics in all_teams_statistics:
        incomplete_series.append(team_statistics["incomplete_seria"])

    series = sorted(series, key=lambda x: x["games"][0], reverse=False)
    incomplete_series = sorted(incomplete_series, key=lambda x: x["games"][0], reverse=False)

    #investigate0(teams, games, series, statistics_by_team)
    investigate1(teams, games, series, statistics_by_team)


def get_marathon_odds():
    data = load_html_page("https://www.marathonbet.ru/su/popular/Ice+Hockey/KHL/", {})
    odds = parse_bet_html(data)
    return enrich_odds(odds)


def print_teams(teams):
    sorted_teams = sorted(teams)
    for team in sorted_teams:
        print u'{' + u'"name":"{}", "alias": ""'.format(team) + u'},'


def investigate_suspicious2(games, odds, aliases):
    print
    print "---== Total Games Count: {} ==---".format(len(games))
    counter = 0
    for game in games:
        try:
            game_signature = build_game_signature(game, aliases)
            odd = find_odd(odds, aliases, game_signature)
            game_suspicious = is_game_suspicious(game, odd, 2.5)
            if game_suspicious != "suspicious_none":
                print u"{} {} - {}".format(game["date"], game['teamA'], game['teamB'])
                date = game["date"].replace('.', '_')

                filename = ""
                probabilities = list()
                alias_a = aliases[game['teamA']].replace(' ', '_')
                alias_b = aliases[game['teamB']].replace(' ', '_')
                if game_suspicious == "suspicious_A":
                    filename = u"{}_{}_{}_a.txt".format(date, alias_a, alias_b)
                    [probabilities.append(x["probA"]) for x in odd["odds"]]
                elif game_suspicious == "suspicious_B":
                    filename = u"{}_{}_{}_b.txt".format(date, alias_a, alias_b)
                    [probabilities.append(x["probB"]) for x in odd["odds"]]

                file_path = os.path.join(games_directory, filename)
                print_list_to_file(file_path, probabilities)
                counter += 1

        except Exception as ex:
            i = 0
            # print ex.args[0]


def is_game_suspicious(game, odd, threshold):
    team_a_xw = 0
    team_b_xw = 0
    for item in odd["odds"]:
        prob_a_xw = item["probA"] + item["probDraw"]
        item_a_xw = 1./prob_a_xw if prob_a_xw != 0 else 0.
        team_a_xw = item_a_xw if item_a_xw > team_a_xw else team_a_xw

        prob_b_xw = item["probB"] + item["probDraw"]
        item_b_xw = 1./prob_b_xw if prob_b_xw != 0 else 0.
        team_b_xw = item_b_xw if item_b_xw > team_b_xw else team_b_xw

    if game["overtime"]:
        if team_a_xw > threshold:
            return "suspicious_A"
        if team_b_xw > threshold:
            return "suspicious_B"

    if team_a_xw > threshold and game["scoreA"] > game["scoreB"]:
        return "suspicious_A"

    if team_b_xw > threshold and game["scoreA"] < game["scoreB"]:
        return "suspicious_B"

    return "suspicious_none"


def find_odd(odds, aliases, game_signature):
    for odd in odds:
        odd_signature = build_odd_signature(odd, aliases)
        if game_signature == odd_signature:
            return odd

    raise Exception("No odd found for game signature '{}'".format(game_signature))


def build_odd_signature(odd, aliases):
    team_a = odd['teamA']
    team_b = odd['teamB']
    alias_a = aliases[team_a]
    alias_b = aliases[team_b]
    date = format_odd_date(odd['date'])

    return "{}_{}_{}".format(alias_a, alias_b, date)


def format_odd_date(date):
    parts = date.split(' ')
    parts = parts[0].split('-')
    return "{}.{}.{}".format(parts[2], parts[1], parts[0])


def build_game_signature(game, aliases):
    team_a = game['teamA']
    team_b = game['teamB']
    alias_a = aliases[team_a]
    alias_b = aliases[team_b]
    date = game['date']

    return "{}_{}_{}".format(alias_a, alias_b, date)


def investigate_suspicious(games, statistics_by_team):
    print
    print "---== Total Games Count: {} ==---".format(len(games))
    threshold = .5
    for game in games:
        team_a = game['teamA']
        team_b = game['teamB']
        score_a = calc_score(team_a, statistics_by_team)
        score_b = calc_score(team_b, statistics_by_team)
        diff = score_a - score_b
        # analyze.printGame(game)
        # print diff
        if (diff > threshold or diff < -threshold) and game['overtime']:
            analyze.printGame(game, "{0:.3f}".format(diff))
            continue
        if (diff > threshold) and game['scoreA'] < game['scoreB']:
            analyze.printGame(game, "{0:.3f}".format(diff))
        if (diff < -threshold) and game['scoreA'] > game['scoreB']:
            analyze.printGame(game, "{0:.3f}".format(diff))


def calc_score(team, statistics_by_team):
    statistics = statistics_by_team[team]
    return float(statistics['score']) / len(statistics['games'])


def vectorsScalarMultiplication(vec0, vec1):
    length = len(vec0) if len(vec0) > len(vec1) else len(vec1)
    result = 0.
    for index in range(0, length):
        result += vec0[index] * vec1[index]
    return result

def modulus(x):
    return x if x > 0 else -x

def sign(x):
    return 1 if x >= 0 else -1

def round(x):
    return int(x + (sign(x) * 0.5))

def printForecastedBets(series, games, teamInfos):
    for seria in series:
        predictedLength_0 = analyze.calculatePredictedLength_0(seria, teamInfos, games)

        teamName = seria["team"]
        info = teamInfos[teamName]
        pointsPerGame = float(info["score"])/len(info["games"])
        drawPerGame = float(info["drawCount"])/len(info["games"])

        # -0.130996156*pointsPerGame + 0.601171399*predictedLength_0 + 0.242028586*drawPerGame
        coeffs = [-0.130996156, 0.601171399, 0.242028586]
        values = [pointsPerGame, predictedLength_0, drawPerGame]
        learningLength = vectorsScalarMultiplication(coeffs, values)

        learningLength = modulus(round(learningLength))

        seriaType = seria["type"]
        seriaLength = len(seria["games"])

        print u'{} ({}/{}/{}):'.format(seria["team"], seriaType, seriaLength, learningLength)
        for gameIndex in seria["games"]:
            game = games[gameIndex]
            win, lose, draw = analyze.getGameOutcome(teamInfos[game["teamA"]], teamInfos[game["teamB"]])
            extension = '{:.3f}/{:.3f}/{:.3f}'.format(win, draw, lose)
            analyze.printGame(game, extension)

        if seria["type"] == GameResult.DRAW:
            print "(-) NO BETS: DRAW SERIA"
        else:
            if pointsPerGame < 0.725 or pointsPerGame > 1.3:
                print "(-) NO BETS: SERIA FOR OUTSTANDING TEAM"
            else:
                if learningLength != seriaLength:
                    print "(-) NO BETS: SERIA IS HIGHLY LIKELY TO BE LONGER OR ENDED"
                else:
                    print "(+) BETS SHOULD BE DONE RIGHT NOW"
        print

def printSeries(series, games, teamInfos):
    for seria in series:
        print u'{} ({}/{}):'.format(seria["team"], seria["type"], len(seria["games"]))
        for gameIndex in seria["games"]:
            game = games[gameIndex]
            win, lose, draw = analyze.getGameOutcome(teamInfos[game["teamA"]], teamInfos[game["teamB"]])
            extension = '{:.3f}/{:.3f}/{:.3f}'.format(win, draw, lose)
            analyze.printGame(game, extension)
        print

def get_liga_stavok_coeff():
    parameters = {
        "t": "11888",
        "g": "topic"
    }
    data = load_html_page("https://www.ligastavok.ru/Topics/Ice-Hockey/t", parameters)
    coeffs = parse_liga_stavok_html(data)
    return enrich_odds(coeffs)

def getRegressionCoeffs(teamIndexes, seriaTypes, teamToIndex, games, series, teamInfos):
    teamScores = list()
    drawScores = list()
    predictedLengths = list()
    signs = list()
    y = list()

    #for index in range(0, len(series)):
    for index in range(1, len(series)*3/4):
        seria = series[index]

        if seria["type"] not in seriaTypes:
            continue

        teamName = seria["team"]
        if teamToIndex[teamName] not in teamIndexes:
            continue

        info = teamInfos[teamName]

        pointsPerGame = float(info["score"])/len(info["games"])
        teamScores.append(pointsPerGame)

        drawPerGame = float(info["drawCount"])/len(info["games"])
        drawScores.append(drawPerGame)

        predictedLength = analyze.calculatePredictedLength_0(seria, teamInfos, games)
        predictedLengths.append(predictedLength)

        length = len(seria["games"]) if seria["type"] == GameResult.WIN else -len(seria["games"])
        y.append(length)

        sign = -1 if length < 0 else 1
        signs.append(sign)

    columns = [
        teamScores,
        drawScores,
        predictedLengths,
        y
    ]
    logColumns(path.join(work_directory, 'extended.txt'), columns)

    whole_data = np.genfromtxt(path.join(work_directory, 'extended.txt'), delimiter=',', filling_values=np.nan)

    data_x = whole_data[:, [0,1,2]]
    data_y = whole_data[:, 3]

    linear_regressor = linear_model.LinearRegression()
    linear_regressor.fit(data_x, data_y)

    linear_regressor.predict(data_x)
    coeff = linear_regressor.coef_

    summ_diff_0 = 0
    length = len(y)
    for index in range(0, length):
        x = [teamScores[index], drawScores[index], predictedLengths[index]]
        predicted_y = x[0]*coeff[0] + x[1]*coeff[1] + x[2]*coeff[2]
        summ_diff_0 += 1.0 if modulus(y[index] - round(predicted_y)) == 0 else 0

    percent = summ_diff_0/length if length != 0 else 0
    return coeff, percent


def investigate1(teams, games, series, teamInfos):
    teams = sorted(teams)

    index = 0
    teamToIndex = dict()
    hist_dif_by_team = dict()
    for team in teams:
        hist_dif_by_team[team] = dict()
        teamToIndex[team] = index
        # print u'{}. {}'.format(index, team)
        index += 1

    for state in [GameResult.WIN, GameResult.LOSE]:
        complex_team_indexes = set()
        results = list()
        for teamA in teams:
            team_a_index = teamToIndex[teamA]
            for teamB in teams:
                team_b_index = teamToIndex[teamB]

                if team_a_index == team_b_index:
                    continue

                if team_a_index < team_b_index:
                    complex_team_index = (team_a_index * 100 + team_b_index)
                else:
                    complex_team_index = (team_b_index * 100 + team_a_index)

                if complex_team_index in complex_team_indexes:
                    continue
                complex_team_indexes.add(complex_team_index)

                regression_coeffs, percent = getRegressionCoeffs([team_a_index, team_b_index], [state],
                                                        teamToIndex, games, series, teamInfos)

                results.append({
                    "teamA": teamA,
                    "teamB": teamB,
                    "percent": percent,
                    "coeffs": regression_coeffs
                })

        print '----==== {} ====----'.format(state)
        # results = sorted(results, key=lambda x:x["percent"], reverse=True)
        # for index in range(0, len(results)):
        #     result = results[index]
        #     if result["percent"] < 0.7:
        #         break
        #     print u"{}. {}/{}:({}) {}".format(index+1, result["teamA"], result["teamB"], result["percent"], result["coeffs"])

        bestResults = dict()
        for result in results:
            teamA = result["teamA"]
            teamB = result["teamB"]
            if teamA not in bestResults or bestResults[teamA]["percent"] < result["percent"]:
                bestResults[teamA] = {
                    "team": teamA,
                    "percent": result["percent"],
                    "coeffs": result["coeffs"]
                }
            if teamB not in bestResults or bestResults[teamB]["percent"] < result["percent"]:
                bestResults[teamB] = {
                    "team": teamB,
                    "percent": result["percent"],
                    "coeffs": result["coeffs"]
                }

        results = sorted(bestResults.values(), key=lambda x:x["percent"], reverse=True)

        index = 1
        full_series_count = 0
        full_matched_series = 0
        for value in results:
            if value["percent"] > 0.72:
                matched_series, series_count = get_production_percent(games, value["team"], teamInfos, state, value["coeffs"])
                if series_count != 0:
                    prod_percent = 1.0*matched_series/series_count
                else:
                    prod_percent = 0.0
                full_series_count += series_count
                full_matched_series += matched_series

                print u"{}. {}:({}/{}/{}) {}".format(index, value["team"], value["percent"], matched_series, series_count, value["coeffs"])
            else:
                print u"{}. {}:({}) {}".format(index, value["team"], value["percent"], value["coeffs"])
            index += 1

        full_percent = full_matched_series/full_series_count if full_series_count != 0 else 0
        print "Production percent through {} games = {}".format(full_series_count, full_percent)

def get_production_percent(games, team_name, team_infos, seria_state, coeff):
    team_info = team_infos[team_name]
    series = team_info["series"]

    series_count = 0
    matched_series = 0

    points_per_game = float(team_info["score"])/len(team_info["games"])
    draw_per_game = float(team_info["drawCount"])/len(team_info["games"])

    for index in range(len(series)*3/4, len(series)):
        seria = series[index]

        if seria_state != seria["type"]:
            continue

        predicted_length = analyze.calculatePredictedLength_0(seria, team_infos, games)
        x = [points_per_game, draw_per_game, predicted_length]
        regression_length = x[0]*coeff[0] + x[1]*coeff[1] + x[2]*coeff[2]

        length = len(seria["games"]) if seria["type"] == GameResult.WIN else -len(seria["games"])
        matched_series += 1.0 if modulus(length - round(regression_length)) == 0 else 0
        series_count += 1.0

    return matched_series, series_count

def investigate0(teams, games, series, teamInfos):
    # {1: 231, 2: 103, 3: 31, 4: 11, 5: 6, 6: 4, 7: 2, 8: 1}
    # {0: 320, 1: 48, 2: 8, 3: 10, 4: 2, 5: 1}
    # Predicted games: 0.822622107969
    teams = sorted(teams)
    teamToIndex = dict()
    index = 0

    hist_dif_by_team = dict()
    for team in teams:
        hist_dif_by_team[team] = dict()
        teamToIndex[team] = index
        print u'{}. {}'.format(index, team)
        index = index + 1

    seriaIndexes = list()
    teamScores = list()
    drawScores = list()
    groupScores0 = list()
    groupScores1 = list()
    groupScores2 = list()
    predictedLengths_0 = list()
    predictedLengths_1 = list()
    learningLengths = list()
    firstGames = list()
    moduls = list()
    signs = list()
    y = list()

    hist_dif = dict()
    hist_len = dict()

    # 0.434850863422
    # 0.483588621444
    supressed_team_indexes = [
         0, # avangard
         1, # avtomobilist
         2, # admiral
         3, # ak bars
         4,
         5, # barys
         6, # vityaz
         7, # dynamo minsk
         8, # dynamo msk
         9, # dynamo riga
        10,
        11, # kun6lun6
        12, # lada
        13, # lokomotive
        # 14, # medveshchak
        15, # metallurg mg
        16, # metallurg nk
        17, # neftehimik
        18, # SKA
        19, # Salovat Ulaev
        20, # severstal
        21, # sibir
        22,
        23, # sochi
        24, # spartak
        25,
        26, # traktor
        27, # CSKA
        28  # ugra
    ]

    for seriaIndex in range(0, len(series)):
        seria = series[seriaIndex]

        if seria["type"] == GameResult.DRAW:
            continue
        if seria["type"] == GameResult.LOSE:
            continue

        teamName = seria["team"]
        teamIndex = teamToIndex[teamName]

        if teamIndex in supressed_team_indexes:
            continue

        info = teamInfos[teamName]
        pointsPerGame = float(info["score"])/len(info["games"])

        gs0 = 0
        gs1 = 0
        gs2 = 0
        # if pointsPerGame < 0.725:
        #     gs0 = 1
        # else:
        #     if pointsPerGame < 1.3:
        #         gs1 = 1
        #     else:
        #         gs2 = 1
        # if gs1 != 1:
        #     continue

        teamScores.append(pointsPerGame)
        seriaIndexes.append(seriaIndex)

        drawPerGame = float(info["drawCount"])/len(info["games"])
        drawScores.append(drawPerGame)

        predictedLength_0 = analyze.calculatePredictedLength_0(seria, teamInfos, games)
        predictedLengths_0.append(predictedLength_0)

        predictedLength_1 = analyze.calculatePredictedLength_1(seria, teamInfos, games)
        predictedLengths_1.append(predictedLength_1)

        groupScores0.append(gs0)
        groupScores1.append(gs1)
        groupScores2.append(gs2)

        length = len(seria["games"]) if seria["type"] == GameResult.WIN else -len(seria["games"])

        y.append(length)

        sign = -1 if length < 0 else 1
        signs.append(sign)

        # [ -1.30996156e-01  -1.33226763e-15   6.01171399e-01   2.69801540e-01]
        # learningLen = -0.130996156*pointsPerGame + 0.601171399*predictedLength_0 + 0.242028586*drawPerGame
        # 0.42107069  0.69343933 -0.43507922 -0.24242128
        # [ 0.4580515   0.68221614 -0.43113222 -0.21630551]
        # [ 0.59852687  0.65419101 -1.34771957 -0.13476879]
        # [ 0.71183332  0.6269543  -1.47520325 -0.07708466]
        # [ 0.70229778  0.6403885  -1.75299342 -0.11191904]
        # [ 0.46267699  0.54079622 -1.21599471  0.13371656]
        # [ 0.28186122  0.53868572 -1.05141883  0.10180103]
        # [ 0.08496853  0.60337722 -0.78299261 -0.05996167] {0: 156, 1: 138, 2: 13, 3: 6, 4: 6, 5: 1, 6: 1, 7: 1}
        # [ 0.44127728  0.74393335 -0.55328241  0.        ] {0: 70, 1: 173, 2: 70, 3: 7, 5: 1, 6: 1}
        # learningLen = 0.08496853*pointsPerGame + 0.60337722*predictedLength_0 - 0.78299261*drawPerGame - 0.05996167*sign
        learningLen = 0*pointsPerGame + 1.*predictedLength_0 - 10.*drawPerGame - 0.0*sign
        learningLengths.append(learningLen)


        firstGame = seria["games"][0]
        firstGames.append(firstGame)

        modul = modulus(learningLen - length)
        modul = round(modul)
        moduls.append(modul)

        team_hist_dif = hist_dif_by_team[teamName]
        if modul in team_hist_dif:
            team_hist_dif[modul] += 1
        else:
            team_hist_dif[modul] = 1

        if modul in hist_dif:
            hist_dif[modul] += 1
        else:
            hist_dif[modul] = 1

        length = len(seria["games"])
        if length in hist_len:
            hist_len[length] += 1
        else:
            hist_len[length] = 1

    print hist_len
    print hist_dif
    print "Predicted games: {}".format(float(hist_dif[0])/len(learningLengths))
    print
    for team_name in hist_dif_by_team.keys():
        team_hist_dif = hist_dif_by_team[team_name]
        summ = 0.
        for value in team_hist_dif.keys():
            summ += team_hist_dif[value]
        ratio = float(team_hist_dif[0])/summ if summ != 0. else 0.
        print u"Predicted games for {}: {}".format(team_name, ratio)

    # logXY(path.join(work_directory, 'score_len.txt'), teamScores, y)
    # logXY(path.join(work_directory, 'pred_len0.txt'), predictedLengths_0, y)
    columns = [
        teamScores,
        groupScores0,
        groupScores1,
        groupScores2,
        predictedLengths_0,
        drawScores,
        signs,
        y,
        firstGames,
        learningLengths,
        moduls
    ]

    valuable_columns = [
        teamScores,
        predictedLengths_0,
        drawScores,
        signs
    ]
    logColumns(path.join(work_directory, 'extended.txt'), columns)

def processSeria(seria, games, teamInfos, predicted, spendings, profit):
    PROFIT = 1.0
    GAMES_STOP_INVEST = 2.5
    GAMES_START_INVEST = -1

    if len(seria["games"]) == 1:
        return profit

    if predicted + GAMES_START_INVEST > len(seria["games"]):
        return profit

    type = seria["type"]
    teamName = seria["team"]
    seriaGames = seria["games"]
    teamInfo = teamInfos[teamName]
    nextGames = analyze.getNextGames(seria["games"][0], teamInfo, games)

    firstGame = int(predicted + GAMES_START_INVEST)
    firstGame = firstGame if firstGame > 1 else 1

    length = int(GAMES_STOP_INVEST - GAMES_START_INVEST)
    length = length if length < len(seriaGames) else len(seriaGames)
    length = length if length < len(nextGames) else len(nextGames)

    seriaSpends = 0.0
    for index in range(0, length):
        indexInGames = nextGames[index + firstGame]
        probability = analyze.getProbabilty(teamName, games[indexInGames], type, teamInfos)
        rest = 1.0 - probability
        spends = (PROFIT + seriaSpends)*rest / (1.0 - rest)

        seriaSpends += spends
        spendings[indexInGames] += spends

    if predicted + GAMES_STOP_INVEST < len(seria["games"]):
        if firstGame + length < len(nextGames):
            indexInGames = nextGames[firstGame + length]
            spendings[indexInGames] -= seriaSpends
        return profit - seriaSpends
    else:
        if firstGame + length < len(nextGames):
            indexInGames = nextGames[firstGame + length]
            spendings[indexInGames] -= seriaSpends
        return profit + PROFIT


def load_games(filename):
    with open(filename, 'r') as rawFile:
        gamesData = rawFile.read().replace('\n', '')

    games = json.loads(gamesData)
    for gameIndex in range(0, len(games)):
        game = games[gameIndex]
        game["index"] = gameIndex
        if game["overtime"] != u'true':
            game["overtime"] = False
            if int(game["scoreA"]) > int(game["scoreB"]):
                game["winner"] = game["teamA"]
                game["loser"] = game["teamB"]
            else:
                game["winner"] = game["teamB"]
                game["loser"] = game["teamA"]
        else:
            game["overtime"] = True

    return games

if __name__ == "__main__":
    main()