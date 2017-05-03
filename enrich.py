import copy

WIN_STATE = {"state": 0, "toString": "WIN"}
LOSE_STATE = {"state": 1, "toString": "LOSE"}
DRAW_STATE = {"state": 2, "toString": "DRAW"}

def hyperbole(x):
    return 1.0/x if x != 0 else 0.


def enrichCoeff(gamesWithCoeff):
    for game in gamesWithCoeff:
        winA = hyperbole(game['winA'])
        winB = hyperbole(game['winB'])
        draw = hyperbole(game['draw'])
        game['winAX'] = hyperbole(winA + draw)
        game['winBX'] = hyperbole(winB + draw)


def enrich_games(games):
    for game in games:
        if not game["overtime"]:
            if int(game["scoreA"]) > int(game["scoreB"]):
                game["winner"] = game["teamA"]
                game["loser"] = game["teamB"]
            else:
                game["winner"] = game["teamB"]
                game["loser"] = game["teamA"]
    return games


def extract_teams(games):
    teams = set()
    for game in games:
        teams.add(game["teamA"])
        teams.add(game["teamB"])
    return teams


def generate_statistics_by_team(teams, games):
    statistics_by_team = dict()
    for team in teams:
        gameCounter = 0
        winCounter = 0
        loseCounter = 0
        drawCounter = 0
        teamGames = list()
        for game in games:
            if team != game["teamA"] and team != game["teamB"]:
                continue
            teamGames.append(game["index"])
            gameCounter = gameCounter + 1
            if game["overtime"]:
                drawCounter = drawCounter + 1
            else:
                if game["winner"] == team:
                    winCounter = winCounter + 1
                else:
                    loseCounter = loseCounter + 1

        statistic = {
            "name": team,
            "winCount": winCounter,
            "loseCount": loseCounter,
            "drawCount": drawCounter,
            "score": winCounter*2 + drawCounter,
            "games": teamGames
        }
        statistics_by_team[team] = statistic

    return statistics_by_team

def filterGamesByTeam(team, games):
    filteredGames = list()
    for game in games:
        if game["teamA"] == team or game["teamB"] == team:
            filteredGames.append(game)
    return filteredGames

def appendSeria(serias, teamName, games, state):
    if len(games) != 0:
        serias.append({
            "team": teamName,
            "type": state["toString"],
            "games": copy.copy(games)
        })


def enrich_by_series(statistics_by_team, games):

    for team in statistics_by_team.keys():
        team_statistics = statistics_by_team[team]
        teamGames = filterGamesByTeam(team, games)

        currentSeria = list()
        currentState = DRAW_STATE
        team_statistics["series"] = list()
        team_statistics["incomplete_seria"] = None

        for game in teamGames:
            gameState = DRAW_STATE
            if not game["overtime"]:
                if game["winner"] == team:
                    gameState = WIN_STATE
                else:
                    gameState = LOSE_STATE

            if currentState["state"] != gameState["state"]:
                appendSeria(team_statistics["series"], team, currentSeria, currentState)
                del currentSeria[:]

            currentState = gameState
            currentSeria.append(game["index"])

        team_statistics["incomplete_seria"] = {
            "team": team,
            "type": currentState["toString"],
            "games": copy.copy(currentSeria)
        }