from api import Log, id_from_logs_url
import json
import sys



def main():
    print(id_from_logs_url('https://logs.tf/3081672#76561197970669109'))
    log = Log(id_from_logs_url(sys.argv[1]))
    scout_medic_combos = get_combos(log)
    for scout in scout_medic_combos:
        score = 0.0
        print(get_alias(log, scout))
        damage_efficiency = calculate_damage_efficiency_score(log, scout)
        print('Damage Efficiency: ' + str(damage_efficiency) + '/25')
        kill_death = calculate_kd_score(log, scout)
        print('Kill/Death: ' + str(kill_death) + '/25')
        med_diff = calculate_med_diff_score(log, scout, scout_medic_combos)
        print('Med Diff: ' + str(med_diff) + '/5')
        med_diff_ratio = calculate_med_diff_ratio_score(log, scout, scout_medic_combos)
        print('Med Diff Ratio: ' + str(med_diff_ratio) + '/5')
        round_diff = calculate_round_diff_score(log, scout)
        print('Round Diff: ' + str(round_diff) + '/5')
        frags = calculate_frag_score(log, scout)
        print('Frags: ' + str(frags) + '/10')
        damage = calculate_damage_score(log, scout)
        print('Damage: ' + str(damage) + '/10')
        kill_participation = calculate_kill_participation_score(log, scout)
        print('Kill Participation: ' + str(kill_participation) + '/10')
        score = damage_efficiency + kill_death + med_diff + round_diff + frags + damage + kill_participation
        heal_efficiency = calculate_heal_percent_effiency_score(log, scout, scout_medic_combos[scout], score)
        print('Heal Efficiency: ' + str(heal_efficiency) + '/5')
        score += heal_efficiency 
        print('Score: ' + str(score) + '/100' + '\n') 

def scale_score(min_value, max_value, max_result, value):
    if value <= min_value:
        return 0.0
    if value >= max_value:
        return max_result

    value_diff = float(max_value - min_value)
    adjusted_value = float(value - min_value)
    return (adjusted_value / value_diff) * max_result

def get_combos(log):
    scout_medic_combos = dict()
    for medic in log.healspread:
        top_heal_scout = ''
        top_heal = 0
        for player in log.healspread[medic]:
            if log.healspread[medic][player] > top_heal and played_scout(log, player):
                top_heal = log.healspread[medic][player]
                top_heal_scout = player
        scout_medic_combos[top_heal_scout] = medic
    return scout_medic_combos


def played_scout(log, player):
    if log.players[player]['class_stats'][0]['type'] == 'scout':
        return True
    else:
        return False    

def calculate_damage_efficiency_score(log, player):
    damage_done = player_stat(log, player, 'dmg')
    damage_taken = player_stat(log, player, 'dt')
    return scale_score(0.5, 2, 25.0, damage_done / damage_taken)

def calculate_kd_score(log, player):
    kills = player_stat(log, player, 'kills')
    deaths = player_stat(log, player, 'deaths')
    return scale_score(0.5, 3.0, 25.0, float(kills) / deaths)

def calculate_med_diff_score(log, player, scout_medic_combos):
    friendly_medic = scout_medic_combos[player]
    enemy_medic = ''
    for scout in scout_medic_combos:
        if scout != player:
            enemy_medic = scout_medic_combos[scout]

    friendly_medic_deaths = player_stat(log, friendly_medic, 'deaths')
    enemy_medic_deaths = player_stat(log, enemy_medic, 'deaths')
    return scale_score(-5, 5, 5, enemy_medic_deaths - friendly_medic_deaths)

def calculate_med_diff_ratio_score(log, player, scout_medic_combos):
    friendly_medic = scout_medic_combos[player]
    enemy_medic = ''
    for scout in scout_medic_combos:
        if scout != player:
            enemy_medic = scout_medic_combos[scout]

    friendly_medic_deaths = player_stat(log, friendly_medic, 'deaths')
    enemy_medic_deaths = player_stat(log, enemy_medic, 'deaths')
    if (friendly_medic_deaths + enemy_medic_deaths) == 0:
        return 5
    return scale_score(0.0, 1.0, 5, 1.0 - ((friendly_medic_deaths) / (friendly_medic_deaths + enemy_medic_deaths)))

def calculate_round_diff_score(log, player):
    player_team = player_stat(log, player, 'team')
    rounds_won = log.teams[player_team]['score']
    opposing_rounds_won = 0
    if player_team == 'Red':
        opposing_rounds_won = log.teams['Blue']['score']
    else:
        opposing_rounds_won = log.teams['Red']['score']
    if rounds_won == 0 and opposing_rounds_won == 0:
        return scale_score(0.0, 1.0, 5.0, .5)
    return scale_score(0.0, 1.0, 5.0, float(rounds_won) / (opposing_rounds_won + rounds_won))

def calculate_frag_score(log, player):
    red_kills = log.teams['Red']['kills']
    blue_kills = log.teams['Blue']['kills']
    kills = player_stat(log, player, 'kills')
    return scale_score(.03, .18, 10, float(kills) / (red_kills + blue_kills))

def calculate_damage_score(log, player):
    red_dmg = log.teams['Red']['dmg']
    blue_dmg = log.teams['Blue']['dmg']
    dmg = player_stat(log, player, 'dmg')
    return scale_score(.03, .15, 10, float(dmg) / (red_dmg + blue_dmg))

def calculate_kill_participation_score(log, player):
    team_kills = log.teams[player_stat(log, player, 'team')]['kills']
    kills = player_stat(log, player, 'kills')
    assists = player_stat(log, player, 'assists')
    return scale_score(.1, .5, 10, float(kills + assists) / team_kills)

def calculate_heal_percent_effiency_score(log, player, medic, other_score):
    return scale_score(.75, 3.0, 5.0, float(other_score) / get_heal_percent(log, player, medic))

def get_heal_percent(log, player, medic):
    heals_received = player_stat(log, player, 'hr')
    heals_total = player_stat(log, medic, 'heal')
    return (float(heals_received) / heals_total) * 100.0 

def player_stat(log, player, stat):
    return log.players[player][stat]

def get_alias(log, player):
    return log.names[player]

main()
