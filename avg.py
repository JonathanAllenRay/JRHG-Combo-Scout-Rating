from api import Log, id_from_logs_url
from score import Score, CSScore
import json
import sys

def main():
    file1 = open(sys.argv[1], 'r')
    count = 0
    score_total = CSScore('', '', empty=True)
    while True:
        # Get next line from file
        line = file1.readline()

        # if line is empty
        # end of file is reached
        if not line:
            break

        log = Log(id_from_logs_url(line))
        combo_scouts = log.get_played_class('scout', 'Red', 'combo')
        combo_scouts += log.get_played_class('scout', 'Blue', 'combo')
        for scout in combo_scouts:
            score = CSScore(line, scout)
            score.calculate_score()
            count += 1
            score_total += score
            print("Log " + str(count))

    score_total.print_data(count)

main()