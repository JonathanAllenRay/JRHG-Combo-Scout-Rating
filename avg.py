from api import Log, id_from_logs_url
from score import Score
import json
import sys

def main():
    file1 = open(sys.argv[1], 'r')
    count = 0
    score_total = Score('', '', empty=True)
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
            score_total += score
            print("Log " + str(count))


    score_total.print_data(count)

main()