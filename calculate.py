from api import Log, id_from_logs_url
from score import Score, CSScore, DMScore
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
            combo_scouts = log.get_played_class('scout', 'Red', 'combo')
            combo_scouts += log.get_played_class('scout', 'Blue', 'combo')
            for scout in combo_scouts:
                score = CSScore(line, scout)
                score.calculate_score()
                score.print_data()
        file1.close()
    else:
        log = Log(id_from_logs_url(sys.argv[1]))
        combo_scouts = log.get_played_class('scout', 'Red', 'combo')
        combo_scouts += log.get_played_class('scout', 'Blue', 'combo')
        for scout in combo_scouts:
            score = CSScore(sys.argv[1], scout)
            score.calculate_score()
            score.print_data()

main()