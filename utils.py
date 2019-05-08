import json


def translate_team_names(teams_structure, aliases_map):
    teams_structure['teamA'] = aliases_map[teams_structure['teamA']]
    teams_structure['teamB'] = aliases_map[teams_structure['teamB']]


def load_aliases(filename):
    with open(filename, 'r') as raw_file:
        aliases_data = raw_file.read().replace('\n', '')

    json_aliases = json.loads(aliases_data)

    aliases = dict()
    for alias in json_aliases:
        aliases[alias["name"]] = alias["alias"]
    return aliases
