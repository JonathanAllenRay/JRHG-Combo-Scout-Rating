from api import Log, id_from_logs_url
import json
import sys

class Score(object):

    def __init__(self, url, player, log=None):
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
        if log == None:
            self.load_log()
        else:
            self.log = log

    def load_log(self):
        self.log = Log(self.log_id)

    def print_data(self):
        print(self.get_alias())
        print('Damage Efficiency: ' + str(round(self.damage_efficiency, 2)) + '/25')
        print('Kill/Death: ' + str(round(self.kill_death, 2)) + '/25')
        print('Med Survivability: ' + str(round(self.med_diff, 2)) + '/5')
        print('Med Survivability (Ratio): ' + str(round(self.med_diff_ratio, 2)) + '/5')
        print('Round Diff: ' + str(round(self.round_diff, 2)) + '/5')
        print('Frags: ' + str(round(self.frags, 2)) + '/10')
        print('Damage: ' + str(round(self.damage, 2)) + '/10')
        print('Kill Participation: ' + str(round(self.kill_participation, 2)) + '/10')
        print('Heal Efficiency: ' + str(round(self.heal_efficiency, 2)) + '/5')
        print('Score: ' + str(round(self.score, 2)) + '/100' + '\n') 

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
        self.score = self.damage_efficiency + self.kill_death + self.med_diff + self.round_diff + self.frags + self.damage + self.kill_participation
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
            return 25.0
        return self.scale_score(0.5, 1.85, 25.0, damage_done / damage_taken)

    def calculate_kd_score(self):
        kills = self.player_stat('kills')
        deaths = self.player_stat('deaths')
        if deaths == 0:
            return 25.0
        return self.scale_score(0.5, 2.85, 25.0, float(kills) / deaths)

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
            return self.scale_score(-5, 5, 5, 0)
        if enemy_medic in self.log.players.keys():
            enemy_medic_deaths = self.log.players[enemy_medic]['deaths']
        else:
            return self.scale_score(-5, 5, 5, 0)

        return self.scale_score(-5, 5, 5, enemy_medic_deaths - friendly_medic_deaths)

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
            return self.scale_score(-5, 5, 5, 0)
        if enemy_medic in self.log.players.keys():
            enemy_medic_deaths = self.log.players[enemy_medic]['deaths']
        else:
            return self.scale_score(-5, 5, 5, 0)

        if (friendly_medic_deaths + enemy_medic_deaths) == 0:
            return 5
        return self.scale_score(0.0, 1.0, 5, 1.0 - ((friendly_medic_deaths) / (friendly_medic_deaths + enemy_medic_deaths)))

    def calculate_round_diff_score(self):
        player_team = self.player_stat('team')
        rounds_won = self.log.teams[player_team]['score']
        opposing_rounds_won = 0
        if player_team == 'Red':
            opposing_rounds_won = self.log.teams['Blue']['score']
        else:
            opposing_rounds_won = self.log.teams['Red']['score']
        if rounds_won == 0 and opposing_rounds_won == 0:
            return self.scale_score(0.0, 1.0, 5.0, .5)
        return self.scale_score(0.0, 1.0, 5.0, float(rounds_won) / (opposing_rounds_won + rounds_won))

    def calculate_frag_score(self):
        red_kills = self.log.teams['Red']['kills']
        blue_kills = self.log.teams['Blue']['kills']
        kills = self.player_stat('kills')
        return self.scale_score(.03, .21, 10, float(kills) / (red_kills + blue_kills))

    def calculate_damage_score(self):
        red_dmg = self.log.teams['Red']['dmg']
        blue_dmg = self.log.teams['Blue']['dmg']
        dmg = self.player_stat('dmg')
        return self.scale_score(.03, .17, 10, float(dmg) / (red_dmg + blue_dmg))

    def calculate_kill_participation_score(self):
        team_kills = self.log.teams[self.player_stat('team')]['kills']
        kills = self.player_stat('kills')
        assists = self.player_stat('assists')
        return self.scale_score(.05, .66, 10, float(kills + assists) / team_kills)

    def calculate_heal_percent_effiency_score(self, medic, other_score):
        return self.scale_score(.70, 3.2, 5.0, float(other_score) / self.get_heal_percent(medic))

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