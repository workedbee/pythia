import json


def translate_team_names(teams_structure, aliases_map):
    if teams_structure['teamA'] in aliases_map:
        teams_structure['teamA'] = aliases_map[teams_structure['teamA']]
    else:
        x = 0
    if teams_structure['teamB'] in aliases_map:
        teams_structure['teamB'] = aliases_map[teams_structure['teamB']]
    else:
        x = 0


def load_aliases(filename):
    with open(filename, 'r') as raw_file:
        aliases_data = raw_file.read().replace('\n', '')

    json_aliases = json.loads(aliases_data)

    aliases = dict()
    for alias in json_aliases:
        aliases[alias["name"]] = alias["alias"]
    return aliases
