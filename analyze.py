from enrich import WIN_STATE, DRAW_STATE, LOSE_STATE

def logMatrix(filename, matrix):
    with open(filename, 'w') as file:
        for row in matrix:
            line = ','.join(row)
            file.write('{}\n'.format(line))

def logColumns(filename, columns):
    with open(filename, 'w') as file:
        columnsCount = len(columns)
        rowsCount = len(columns[0]) if columnsCount != 0 else 0
        for rowIndex in range(0, rowsCount):
            values = list()
            for columnIndex in range(0, columnsCount):
                values.append(str(columns[columnIndex][rowIndex]))
            line = ','.join(values)
            file.write('{}\n'.format(line))

def logXY(filename, x, y):
    with open(filename, 'w') as file:
        index = 0
        for elem in x:
            file.write('{} {}\n'.format(elem, y[index]))
            index = index + 1

def getNextGames(firstGame, teamInfo, games):
    team = teamInfo["name"]
    result_games = list()
    for index in range(0, len(games)):
        game = games[index]
        if firstGame <= game['index'] and (game['teamA'] == team or game['teamB'] == team):
            result_games.append(index)
    return result_games

def getProbabilty(team, game, type, teamInfos):
    winA, winB, draw = getGameOutcome(teamInfos[game["teamA"]], teamInfos[game["teamB"]])
    if team == game["teamA"] and type == WIN_STATE["toString"]:
        return winA
    if team == game["teamB"] and type == WIN_STATE["toString"]:
        return winB
    if team == game["teamA"] and type == LOSE_STATE["toString"]:
        return winB
    if team == game["teamB"] and type == LOSE_STATE["toString"]:
        return winA

def covertCombinationToCoefficients(value, result_length, divider):
    result = [0] * result_length
    for i in range(0, result_length):
        result[i] = value % divider
        value /= divider
    return result

def getRegressionParameters(start_coeff, x_columns, y, precision):
    cx = len(x_columns)
    cy = len(y)
    combination_count = 1
    for i in range(0, cx):
        combination_count *= 21

    step = 1.
    result_coeff = start_coeff
    min_summ = float("inf")
    min_coeff = result_coeff

    for precision_step in range(0, precision):
        for combination in range(0, combination_count):
            coeffs = covertCombinationToCoefficients(combination, cx, 21)
            temp_coeff = list(result_coeff)
            for i in range(0, cx):
                temp_coeff[i] += (coeffs[i]-10) * step
            summ = 0.
            for iy in range(0, cy):
                y_predicted = 0.
                for ix in range(0, cx):
                    y_predicted += temp_coeff[ix] * x_columns[ix][iy]

                y_predicted = round(y_predicted)
                summ += (y[iy] - y_predicted)*(y[iy] - y_predicted)
                if summ > min_summ:
                    break

            if summ < min_summ:
                min_summ = summ
                min_coeff = temp_coeff

        result_coeff = min_coeff
        step = step / 10

    return min_coeff

def calculatePredictedLength_0(seria, teamInfos, games):
    type = seria["type"]
    if type == DRAW_STATE["toString"]:
        return 0

    team = seria["team"]
    teamInfo = teamInfos[team]
    firstGame = seria["games"][0]
    lastGames = getNextGames(firstGame, teamInfo, games)
    lastGames = lastGames[1:]

    averageLength = 1
    length = 2
    seriaProbability = 1.0
    for gameIndex in lastGames:
        game = games[gameIndex]
        probability = getProbabilty(team, game, type, teamInfos)
        seriaProbability = seriaProbability * probability
        averageLength = averageLength + seriaProbability*length

        length = length + 1
        if seriaProbability*length < 0.10:
            break

    if type == LOSE_STATE["toString"]:
        averageLength = -averageLength

    return averageLength


def calculatePredictedLength_1(seria, teamInfos, games):
    type = seria["type"]
    if type == DRAW_STATE["toString"]:
        return 0

    team = seria["team"]
    teamInfo = teamInfos[team]
    firstGame = seria["games"][0]
    lastGames = getNextGames(firstGame, teamInfo, games)
    lastGames = lastGames[1:]

    length = 1
    for gameIndex in lastGames:
        game = games[gameIndex]
        probability = getProbabilty(team, game, type, teamInfos)

        opponentTeam = game["teamA"] if team != game["teamA"] else game["teamB"]
        opponentProbability = getProbabilty(opponentTeam, game, type, teamInfos)

        if type == WIN_STATE["toString"] and probability < opponentProbability:
            break
        if type == LOSE_STATE["toString"] and probability > opponentProbability:
            break

        length = length + 1

    if type == LOSE_STATE["toString"]:
        length = -length

    return length

def printSeriesStatistics(series):
    maxWin = 0
    maxDraw = 0
    maxLose = 0
    for seria in series:
        if seria["type"] == WIN_STATE["toString"]:
            if len(seria["games"]) > maxWin:
                maxWin = len(seria["games"])
        if seria["type"] == DRAW_STATE["toString"]:
            if len(seria["games"]) > maxDraw:
                maxDraw = len(seria["games"])
        if seria["type"] == LOSE_STATE["toString"]:
            if len(seria["games"]) > maxLose:
                maxLose = len(seria["games"])
    print 'WIN/DRAW/LOSE: {}/{}/{}'.format(maxWin, maxDraw, maxLose)


def printGame(game, extension = ""):
    overtime = "OT" if game["overtime"] else ""
    print u"{}. {}:{} {} {} - {} {}".format(game["index"], game["scoreA"], game["scoreB"], overtime, game["teamA"], game["teamB"], extension)

def getGameOutcome(teamA, teamB):
    HOME_ADVANTAGE = 0.07
    DRAW_PROBABILITY = 0.12

    winA = teamA["winCount"]
    loseA = teamA["loseCount"]
    drawA = teamA["drawCount"]

    winB = teamB["winCount"]
    loseB = teamB["loseCount"]
    drawB = teamB["drawCount"]

    gamesCountA = winA + loseA + drawA
    gamesCountB = winB + loseB + drawB

    if gamesCountA == 0 or gamesCountB == 0:
        drawFactor = DRAW_PROBABILITY
        p = 0.5 * (1.0 - drawFactor)
        return p + HOME_ADVANTAGE, p - HOME_ADVANTAGE, drawFactor
    else:
        drawFactor = (float(drawA)/gamesCountA + float(drawB)/gamesCountB)/2.0
        winAProb = float(winA*2 + drawA)/gamesCountA
        winBProb = float(winB*2 + drawB)/gamesCountB
        if winAProb == 0.0 and winBProb == 0.0:
            p = 0.5 * (1.0 - drawFactor)
            return p + HOME_ADVANTAGE, p - HOME_ADVANTAGE, drawFactor

        else:
            winAProb = 0.01 if winAProb == 0.0 else winAProb # to prevent zero probabilty
            winBProb = 0.01 if winBProb == 0.0 else winBProb # to prevent zero probabilty
            winAFactor = (1.0 - drawFactor)*winAProb/(winAProb + winBProb)
            winBFactor = (1.0 - drawFactor)*winBProb/(winAProb + winBProb)
            return winAFactor + HOME_ADVANTAGE, winBFactor - HOME_ADVANTAGE , drawFactor
