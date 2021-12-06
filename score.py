from api import Log, id_from_logs_url
import json
import sys

#CONSTANTS (which aren't really constant)
ROUNDING_PLACES = 2
DE_TOTAL = 25.0
KD_TOTAL = 25.0
FRAGS_TOTAL = 10.0
MED_DIFF_TOTAL = 5.0
MED_DIFF_RATIO_TOTAL = 5.0
ROUND_DIFF_TOTAL = 5.0
HE_TOTAL = 5.0
DAMAGE_TOTAL = 10.0
KP_TOTAL = 10.0
DE_MIN = 0.5
KD_MIN = 0.5
FRAGS_MIN = .03
MED_DIFF_MIN = -5.0
MED_DIFF_RATIO_MIN = 0.0
ROUND_DIFF_MIN = 0.0
HE_MIN = 0.7
DAMAGE_MIN = 0.03
KP_MIN = .1
SCORE_MIN = 100.0
DE_MAX = 1.8
KD_MAX = 2.75
FRAGS_MAX = .2
MED_DIFF_MAX = 5.0
MED_DIFF_RATIO_MAX = 1.0
ROUND_DIFF_MAX = 1.0
HE_MAX = 3.25
DAMAGE_MAX = .16
KP_MAX = .6
SCORE_TOTAL = 100.0

class Score(object):

    def __init__(self, url, player, log=None, empty=False):
        self.player = player
        self.log_id = id_from_logs_url(url)
        self.log = None
        self.score = 0.0
        self.damage_efficiency = 0.0
        self.kill_death = 0.0
        self.med_diff = 0.0
        self.med_diff_ratio = 0.0
        self.round_diff = 0.0
        self.frags = 0.0
        self.damage = 0.0
        self.kill_participation = 0.0
        self.heal_efficiency = 0.0
        if log == None and not empty:
            self.load_log()
        elif not empty:
            self.log = log

    def load_log(self):
        self.log = Log(self.log_id)

    def print_alias(self):
        print(self.get_alias())

    def game_type(self):
        if log is not None:
            return self.log.game_type()
        else:
            return None

    def print_data(self, divisor=1.0):
        if divisor <= 0:
            divisor = 1
        print('Damage Efficiency: ' + str(round(self.damage_efficiency / divisor, ROUNDING_PLACES)) + '/' + str(DE_TOTAL))
        print('Kill/Death: ' + str(round(self.kill_death / divisor, ROUNDING_PLACES)) + '/' + str(KD_TOTAL))
        print('Med Survivability: ' + str(round(self.med_diff / divisor, ROUNDING_PLACES)) + '/' + str(MED_DIFF_TOTAL))
        print('Med Survivability (Ratio): ' + str(round(self.med_diff_ratio / divisor, ROUNDING_PLACES)) + '/' + str(MED_DIFF_RATIO_TOTAL))
        print('Round Diff: ' + str(round(self.round_diff / divisor, ROUNDING_PLACES)) + '/' + str(ROUND_DIFF_TOTAL))
        print('Frags: ' + str(round(self.frags / divisor, ROUNDING_PLACES)) + '/' + str(FRAGS_TOTAL))
        print('Damage: ' + str(round(self.damage / divisor, ROUNDING_PLACES)) + '/' + str(DAMAGE_TOTAL))
        print('Kill Participation: ' + str(round(self.kill_participation / divisor, ROUNDING_PLACES)) + '/' + str(KP_TOTAL))
        print('Heal Efficiency: ' + str(round(self.heal_efficiency / divisor, ROUNDING_PLACES)) + '/' + str(HE_TOTAL))
        print('Score: ' + str(round(self.score / divisor, ROUNDING_PLACES)) + '/' + str(SCORE_TOTAL) + '\n') 

    def __add__(self, other_score):
        self.damage_efficiency += other_score.damage_efficiency
        self.kill_death += other_score.kill_death
        self.med_diff += other_score.med_diff
        self.med_diff_ratio += other_score.med_diff_ratio
        self.round_diff += other_score.round_diff
        self.frags += other_score.frags
        self.damage += other_score.damage
        self.kill_participation += other_score.kill_participation
        self.heal_efficiency += other_score.heal_efficiency
        self.score += other_score.score
        return self

    def calculate_score(self):
        scout_medic_combos = self.log.get_scout_medic_combos()
        self.damage_efficiency = self.calculate_damage_efficiency_score()
        self.kill_death = self.calculate_kd_score()
        self.med_diff = self.calculate_med_diff_score(scout_medic_combos)
        self.med_diff_ratio = self.calculate_med_diff_ratio_score(scout_medic_combos)
        self.round_diff = self.calculate_round_diff_score()
        self.frags = self.calculate_frag_score()
        self.damage = self.calculate_damage_score()
        self.kill_participation = self.calculate_kill_participation_score()
        self.score = self.damage_efficiency + self.kill_death + self.med_diff + self.med_diff_ratio + self.round_diff + self.frags + self.damage + self.kill_participation
        self.heal_efficiency = self.calculate_heal_percent_effiency_score(scout_medic_combos[self.player], self.score)
        self.score += self.heal_efficiency 
        #self.adjust_for_daniel_z()

    def adjust_for_daniel_z(self):
        if self.player == '[U:1:107876215]':
            self.damage_efficiency = 0.0
            self.kill_death = -1.0
            self.med_diff = -69.69
            self.med_diff_ratio = -420.69
            self.round_diff = -80085.69
            self.frags = 0.0001
            self.damage = 0.0
            self.kill_participation = -9000.69420
            self.heal_efficiency = -101.01 
            self.score = self.damage_efficiency + self.kill_death + self.med_diff + self.round_diff + self.frags + self.damage + self.kill_participation + self.heal_efficiency

    def scale_score(self, min_value, max_value, max_result, value):
        if value <= min_value:
            return 0.0
        if value >= max_value:
            return max_result

        value_diff = float(max_value - min_value)
        adjusted_value = float(value - min_value)
        return (adjusted_value / value_diff) * max_result


    def calculate_damage_efficiency_score(self):
        damage_done = self.player_stat('dmg')
        damage_taken = self.player_stat('dt')
        if damage_taken == 0:
            return DE_MAX
        return self.scale_score(DE_MIN, DE_MAX, DE_TOTAL, damage_done / damage_taken)

    def calculate_kd_score(self):
        kills = self.player_stat('kills')
        deaths = self.player_stat('deaths')
        if deaths == 0:
            return KD_MAX
        return self.scale_score(KD_MIN, KD_MAX, KD_TOTAL, float(kills) / deaths)

    def calculate_med_diff_score(self, scout_medic_combos):
        friendly_medic = scout_medic_combos[self.player]
        enemy_medic = ''
        for scout in scout_medic_combos:
            if scout != self.player:
                enemy_medic = scout_medic_combos[scout]

        friendly_medic_deaths = 0
        enemy_medic_deaths = 0
        if friendly_medic in self.log.players.keys():
            friendly_medic_deaths = self.log.players[friendly_medic]['deaths']
        else:
            return self.scale_score(MED_DIFF_MIN, MED_DIFF_MAX, MED_DIFF_TOTAL, 0)
        if enemy_medic in self.log.players.keys():
            enemy_medic_deaths = self.log.players[enemy_medic]['deaths']
        else:
            return self.scale_score(MED_DIFF_MIN, MED_DIFF_MAX, MED_DIFF_TOTAL, 0)

        return self.scale_score(MED_DIFF_MIN, MED_DIFF_MAX, MED_DIFF_TOTAL, enemy_medic_deaths - friendly_medic_deaths)

    def calculate_med_diff_ratio_score(self, scout_medic_combos):
        friendly_medic = scout_medic_combos[self.player]
        enemy_medic = ''
        for scout in scout_medic_combos:
            if scout != self.player:
                enemy_medic = scout_medic_combos[scout]

        friendly_medic_deaths = 0
        enemy_medic_deaths = 0
        if friendly_medic in self.log.players.keys():
            friendly_medic_deaths = self.log.players[friendly_medic]['deaths']
        else:
            return self.scale_score(MED_DIFF_MIN, MED_DIFF_MAX, MED_DIFF_TOTAL, 0)
        if enemy_medic in self.log.players.keys():
            enemy_medic_deaths = self.log.players[enemy_medic]['deaths']
        else:
            return self.scale_score(MED_DIFF_MIN, MED_DIFF_MAX, MED_DIFF_TOTAL, 0)

        if (friendly_medic_deaths + enemy_medic_deaths) == 0:
            return MED_DIFF_RATIO_MAX
        return self.scale_score(MED_DIFF_RATIO_MIN, MED_DIFF_RATIO_MAX, MED_DIFF_RATIO_TOTAL, 1.0 - ((friendly_medic_deaths) / (friendly_medic_deaths + enemy_medic_deaths)))

    def calculate_round_diff_score(self):
        player_team = self.player_stat('team')
        rounds_won = self.log.teams[player_team]['score']
        opposing_rounds_won = 0
        if player_team == 'Red':
            opposing_rounds_won = self.log.teams['Blue']['score']
        else:
            opposing_rounds_won = self.log.teams['Red']['score']
        if rounds_won == 0 and opposing_rounds_won == 0:
            return self.scale_score(ROUND_DIFF_MIN, ROUND_DIFF_MAX, ROUND_DIFF_TOTAL, .5)
        return self.scale_score(ROUND_DIFF_MIN, ROUND_DIFF_MAX, ROUND_DIFF_TOTAL, float(rounds_won) / (opposing_rounds_won + rounds_won))

    def calculate_frag_score(self):
        red_kills = self.log.teams['Red']['kills']
        blue_kills = self.log.teams['Blue']['kills']
        kills = self.player_stat('kills')
        return self.scale_score(FRAGS_MIN, FRAGS_MAX, FRAGS_TOTAL, float(kills) / (red_kills + blue_kills))

    def calculate_damage_score(self):
        red_dmg = self.log.teams['Red']['dmg']
        blue_dmg = self.log.teams['Blue']['dmg']
        dmg = self.player_stat('dmg')
        return self.scale_score(DAMAGE_MIN, DAMAGE_MAX, DAMAGE_TOTAL, float(dmg) / (red_dmg + blue_dmg))

    def calculate_kill_participation_score(self):
        team_kills = self.log.teams[self.player_stat('team')]['kills']
        kills = self.player_stat('kills')
        assists = self.player_stat('assists')
        return self.scale_score(KP_MIN, KP_MAX, KP_TOTAL, float(kills + assists) / team_kills)

    def calculate_heal_percent_effiency_score(self, medic, other_score):
        return self.scale_score(HE_MIN, HE_MAX, HE_TOTAL, float(other_score) / self.get_heal_percent(medic))

    def get_heal_percent(self, medic):
        heals_received = self.player_stat('hr')
        heals_total = 0.0
        if medic in self.log.players.keys():
            heals_total = self.log.players[medic]['heal']
        else:
            return 20.00 #Safe estimate
        return (float(heals_received) / heals_total) * 100.0 

    def player_stat(self, stat):
        return self.log.players[self.player][stat]

    def get_alias(self):
        return self.log.names[self.player]

def score_summary(score):
    if score <= 10.00:
        return "Apocalyptic"
    if score <= 20.00:
        return "Terrible"
    if score <= 30.00:
        return "Bad"
    if score <= 40.00:
        return "Poor"
    if score <= 45.00:
        return "Sub-Par"
    if score <= 55.00:
        return "Average"
    if score <= 60.00:
        return "Good"
    if score <= 65.00:
        return "Great"
    if score <= 70.00:
        return "Very Good"
    if score <= 80.00:
        return "Excellent"
    if score <= 90.00:
        return "Masterful"
    if score <= 99.99:
        return "Ascended"
    if score == 100.00:
        return "Perfect"