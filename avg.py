from api import Log, id_from_logs_url
from score import Score
import json
import sys

def main():
    file1 = open(sys.argv[1], 'r')
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
    while True:
        # Get next line from file
        line = file1.readline()

        # if line is empty
        # end of file is reached
        if not line:
            break

        log = Log(id_from_logs_url(line))
        scout_medic_combos = log.get_scout_medic_combos()
        for scout in scout_medic_combos:
            score = Score(line, scout)
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
    file1.close()


main()