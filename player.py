from api import Log, LogList, id_from_logs_url
from score import Score
import json
import sys

def main():
    log_number = 0
    count = 0
    score_total = 0.0
    damage_efficiency = 0.0
    kill_death = 0.0
    med_diff = 0.0
    med_diff_ratio = 0.0
    round_diff = 0.0
    frags = 0.0
    damage = 0.0
    kill_participation = 0.0
    heal_efficiency = 0.0
    log_list = LogList(player=sys.argv[1], limit=sys.argv[2], offset=sys.argv[3])
    other_steam_id = sys.argv[4]
    for log in log_list.logs:
        log_number += 1
        print('Log # ' + str(log_number) + '/' + str(len(log_list.logs)))
        next_log = Log(log['id'])
        scout_medic_combos = next_log.get_scout_medic_combos()
        if other_steam_id in scout_medic_combos.keys():
            score = Score('', other_steam_id, log=next_log)
            score.calculate_score()
            count += 1
            score_total += score.score
            damage_efficiency += score.damage_efficiency
            kill_death += score.kill_death
            med_diff += score.med_diff
            med_diff_ratio += score.med_diff_ratio
            round_diff += score.round_diff
            frags += score.frags
            damage += score.damage
            kill_participation += score.kill_participation
            heal_efficiency += score.heal_efficiency
    print('Damage Efficiency: ' + str(round(damage_efficiency / count, 2)) + '/25')
    print('Kill/Death: ' + str(round(kill_death / count, 2)) + '/25')
    print('Med Survivability: ' + str(round(med_diff / count, 2)) + '/5')
    print('Med Survivability (Ratio): ' + str(round(med_diff_ratio / count, 2)) + '/5')
    print('Round Diff: ' + str(round(round_diff / count, 2)) + '/5')
    print('Frags: ' + str(round(frags / count, 2)) + '/10')
    print('Damage: ' + str(round(damage / count, 2)) + '/10')
    print('Kill Participation: ' + str(round(kill_participation / count, 2)) + '/10')
    print('Heal Efficiency: ' + str(round(heal_efficiency / count, 2)) + '/5')
    print('Score: ' + str(round(score_total / count, 2)) + '/100' + '\n')

main()