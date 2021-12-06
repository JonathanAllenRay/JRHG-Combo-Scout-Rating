from api import Log, LogList, id_from_logs_url
from score import Score, CSScore
import json
import sys

def main():
    log_number = 0
    count = 0
    if sys.argv[1] == "-f":
        file1 = open(sys.argv[2], 'r')
        player = sys.argv[3]
        score_total = CSScore('', player, empty=True)
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
                if player == scout and log.game_type() == "6":
                    print("Calculating log " + line)
                    score = CSScore(line, player)
                    score.calculate_score()
                    count += 1
                    score_total += score
        file1.close()
    else:   
        log_list = LogList(player=sys.argv[1], limit=sys.argv[2], offset=sys.argv[3])
        other_steam_id = sys.argv[4]
        score_total = CSScore('', other_steam_id, empty=True)
        for log in log_list.logs:
            log_number += 1
            print('Log # ' + str(log_number) + '/' + str(len(log_list.logs)))
            next_log = Log(log['id'])
            combo_scouts = next_log.get_played_class('scout', 'Red', 'combo')
            combo_scouts += next_log.get_played_class('scout', 'Blue', 'combo')
            if other_steam_id in combo_scouts and next_log.game_type() == "6":
                score = CSScore('', other_steam_id, log=next_log)
                score.calculate_score()
                count += 1
                score_total += score
            else:
                print("Skipped log.")
    score_total.print_data(count)

main()