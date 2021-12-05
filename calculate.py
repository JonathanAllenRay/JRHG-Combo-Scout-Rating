from api import Log, id_from_logs_url
from score import Score
import json
import sys

def main():
    if sys.argv[1] == 'file':
        file1 = open(sys.argv[2], 'r')
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
                score.print_data()
        file1.close()
    else:
        log = Log(id_from_logs_url(sys.argv[1]))
        scout_medic_combos = log.get_scout_medic_combos()
        for scout in scout_medic_combos:
            score = Score(sys.argv[1], scout)
            score.calculate_score()
            score.print_data()

main()