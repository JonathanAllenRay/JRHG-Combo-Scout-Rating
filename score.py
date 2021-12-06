from api import Log, id_from_logs_url
import json
import sys

#CONSTANTS (which aren't really constant)
ROUNDING_PLACES = 2
SCORE_TOTAL = 100.0

class Score(object):

    def __init__(self, url, player, log=None, empty=False):
        self.player = player
        self.log_id = id_from_logs_url(url)
        self.log = None
        self.score = 0.0
        self.damage_efficiency = 0.0
        self.kill_death = 0.0
        self.round_diff = 0.0
        self.frags = 0.0
        self.damage = 0.0
        self.kill_participation = 0.0
        self.heal_efficiency = 0.0
        self.deaths = 0.0
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

    def scale_score(self, min_value, max_value, max_result, value):
        if value <= min_value:
            return 0.0
        if value >= max_value:
            return max_result

        value_diff = float(max_value - min_value)
        adjusted_value = float(value - min_value)
        return (adjusted_value / value_diff) * max_result

    def calculate_death_score(self, minimum, maximum, total):
        red_kills = self.log.teams['Red']['kills']
        blue_kills = self.log.teams['Blue']['kills']
        deaths = self.player_stat('deaths')
        return self.scale_score(minimum, maximum, total, 1.0 - (float(deaths) / (red_kills + blue_kills)))

    def calculate_damage_efficiency_score(self, minimum, maximum, total):
        damage_done = self.player_stat('dmg')
        damage_taken = self.player_stat('dt')
        if damage_taken == 0:
            return DE_MAX
        return self.scale_score(minimum, maximum, total, damage_done / damage_taken)

    def calculate_kd_score(self, minimum, maximum, total):
        kills = self.player_stat('kills')
        deaths = self.player_stat('deaths')
        if deaths == 0:
            return maximum
        return self.scale_score(minimum, maximum, total, float(kills) / deaths)

    def calculate_round_diff_score(self, minimum, maximum, total):
        player_team = self.player_stat('team')
        rounds_won = self.log.teams[player_team]['score']
        opposing_rounds_won = 0
        if player_team == 'Red':
            opposing_rounds_won = self.log.teams['Blue']['score']
        else:
            opposing_rounds_won = self.log.teams['Red']['score']
        if rounds_won == 0 and opposing_rounds_won == 0:
            return self.scale_score(minimum, maximum, total, .5)
        return self.scale_score(minimum, maximum, total, float(rounds_won) / (opposing_rounds_won + rounds_won))

    def calculate_frag_score(self, minimum, maximum, total):
        red_kills = self.log.teams['Red']['kills']
        blue_kills = self.log.teams['Blue']['kills']
        kills = self.player_stat('kills')
        return self.scale_score(minimum, maximum, total, float(kills) / (red_kills + blue_kills))

    def calculate_damage_score(self, minimum, maximum, total):
        red_dmg = self.log.teams['Red']['dmg']
        blue_dmg = self.log.teams['Blue']['dmg']
        dmg = self.player_stat('dmg')
        return self.scale_score(minimum, maximum, total, float(dmg) / (red_dmg + blue_dmg))

    def calculate_kill_participation_score(self, minimum, maximum, total):
        team_kills = self.log.teams[self.player_stat('team')]['kills']
        kills = self.player_stat('kills')
        assists = self.player_stat('assists')
        return self.scale_score(minimum, maximum, total, float(kills + assists) / team_kills)

    def calculate_heal_percent_effiency_score(self, medic, other_score, minimum, maximum, total):
        return self.scale_score(minimum, maximum, total, float(other_score) / self.get_heal_percent(medic))

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
        if self.log != None and self.player in self.log.names:
            return self.log.names[self.player]
        return 'No Alias Found'


class CSScore(Score):

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

    def __init__(self, url, player, log=None, empty=False):
        super().__init__(url, player, log, empty)
        self.med_diff = 0.0
        self.med_diff_ratio = 0.0

    def print_data(self, divisor=1.0):
        if divisor <= 0:
            divisor = 1
        self.print_alias()
        print('Damage Efficiency: ' + str(round(self.damage_efficiency / divisor, ROUNDING_PLACES)) + '/' + str(CSScore.DE_TOTAL))
        print('Kill/Death: ' + str(round(self.kill_death / divisor, ROUNDING_PLACES)) + '/' + str(CSScore.KD_TOTAL))
        print('Med Survivability: ' + str(round(self.med_diff / divisor, ROUNDING_PLACES)) + '/' + str(CSScore.MED_DIFF_TOTAL))
        print('Med Survivability (Ratio): ' + str(round(self.med_diff_ratio / divisor, ROUNDING_PLACES)) + '/' + str(CSScore.MED_DIFF_RATIO_TOTAL))
        print('Round Diff: ' + str(round(self.round_diff / divisor, ROUNDING_PLACES)) + '/' + str(CSScore.ROUND_DIFF_TOTAL))
        print('Frags: ' + str(round(self.frags / divisor, ROUNDING_PLACES)) + '/' + str(CSScore.FRAGS_TOTAL))
        print('Damage: ' + str(round(self.damage / divisor, ROUNDING_PLACES)) + '/' + str(CSScore.DAMAGE_TOTAL))
        print('Kill Participation: ' + str(round(self.kill_participation / divisor, ROUNDING_PLACES)) + '/' + str(CSScore.KP_TOTAL))
        print('Heal Efficiency: ' + str(round(self.heal_efficiency / divisor, ROUNDING_PLACES)) + '/' + str(CSScore.HE_TOTAL))
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
        self.damage_efficiency = self.calculate_damage_efficiency_score(CSScore.DE_MIN, CSScore.DE_MAX, CSScore.DE_TOTAL)
        self.kill_death = self.calculate_kd_score(CSScore.KD_MIN, CSScore.KD_MAX, CSScore.KD_TOTAL)
        self.med_diff = self.calculate_med_diff_score(scout_medic_combos, CSScore.MED_DIFF_MIN, CSScore.MED_DIFF_MAX, CSScore.MED_DIFF_TOTAL)
        self.med_diff_ratio = self.calculate_med_diff_ratio_score(scout_medic_combos, CSScore.MED_DIFF_RATIO_MIN, CSScore.MED_DIFF_RATIO_MAX, CSScore.MED_DIFF_RATIO_TOTAL)
        self.round_diff = self.calculate_round_diff_score(CSScore.ROUND_DIFF_MIN, CSScore.ROUND_DIFF_MAX, CSScore.ROUND_DIFF_TOTAL)
        self.frags = self.calculate_frag_score(CSScore.FRAGS_MIN, CSScore.FRAGS_MAX, CSScore.FRAGS_TOTAL)
        self.damage = self.calculate_damage_score(CSScore.DAMAGE_MIN, CSScore.DAMAGE_MAX, CSScore.DAMAGE_TOTAL)
        self.kill_participation = self.calculate_kill_participation_score(CSScore.KP_MIN, CSScore.KP_MAX, CSScore.KP_TOTAL)
        self.score = self.damage_efficiency + self.kill_death + self.med_diff + self.med_diff_ratio + self.round_diff + self.frags + self.damage + self.kill_participation
        self.heal_efficiency = self.calculate_heal_percent_effiency_score(scout_medic_combos[self.player], self.score, CSScore.HE_MIN, CSScore.HE_MAX, CSScore.HE_TOTAL)
        self.score += self.heal_efficiency 

    def calculate_med_diff_score(self, scout_medic_combos, minimum, maximum, total):
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
            return self.scale_score(minimum, maximum, total, 0)
        if enemy_medic in self.log.players.keys():
            enemy_medic_deaths = self.log.players[enemy_medic]['deaths']
        else:
            return self.scale_score(minimum, maximum, total, 0)

        return self.scale_score(minimum, maximum, total, enemy_medic_deaths - friendly_medic_deaths)

    def calculate_med_diff_ratio_score(self, scout_medic_combos, minimum, maximum, total):
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
            return self.scale_score(minimum, maximum, total, .5)
        if enemy_medic in self.log.players.keys():
            enemy_medic_deaths = self.log.players[enemy_medic]['deaths']
        else:
            return self.scale_score(minimum, maximum, total, .5)

        if (friendly_medic_deaths + enemy_medic_deaths) == 0:
            return total
        return self.scale_score(minimum, maximum, total, 1.0 - ((friendly_medic_deaths) / (friendly_medic_deaths + enemy_medic_deaths)))

class DMScore(Score):

    DE_TOTAL = 25.0
    KD_TOTAL = 20.0
    FRAGS_TOTAL = 10.0
    ROUND_DIFF_TOTAL = 5.0
    HE_TOTAL = 5.0
    DAMAGE_TOTAL = 20.0
    KP_TOTAL = 5.0
    DEATHS_TOTAL = 10.0
    DE_MIN = 0.5
    KD_MIN = 0.5
    FRAGS_MIN = .03
    ROUND_DIFF_MIN = 0.0
    HE_MIN = 0.7
    DAMAGE_MIN = 0.03
    KP_MIN = .1
    DEATHS_MIN = 0.01
    DE_MAX = 1.8
    KD_MAX = 2.75
    FRAGS_MAX = .2
    ROUND_DIFF_MAX = 1.0
    HE_MAX = 3.25
    DAMAGE_MAX = .16
    KP_MAX = .6
    DEATHS_MAX = 1.0

    def __init__(self, url, player, log=None, empty=False):
        super().__init__(url, player, log, empty)

    def print_data(self, divisor=1.0):
        if divisor <= 0:
            divisor = 1
        self.print_alias()
        print('Damage Efficiency: ' + str(round(self.damage_efficiency / divisor, ROUNDING_PLACES)) + '/' + str(DMScore.DE_TOTAL))
        print('Kill/Death: ' + str(round(self.kill_death / divisor, ROUNDING_PLACES)) + '/' + str(DMScore.KD_TOTAL))
        print('Round Diff: ' + str(round(self.round_diff / divisor, ROUNDING_PLACES)) + '/' + str(DMScore.ROUND_DIFF_TOTAL))
        print('Frags: ' + str(round(self.frags / divisor, ROUNDING_PLACES)) + '/' + str(DMScore.FRAGS_TOTAL))
        print('Damage: ' + str(round(self.damage / divisor, ROUNDING_PLACES)) + '/' + str(DMScore.DAMAGE_TOTAL))
        print('Kill Participation: ' + str(round(self.kill_participation / divisor, ROUNDING_PLACES)) + '/' + str(DMScore.KP_TOTAL))
        print('Heal Efficiency: ' + str(round(self.heal_efficiency / divisor, ROUNDING_PLACES)) + '/' + str(DMScore.HE_TOTAL))
        print('Survival: ' + str(round(self.deaths / divisor, ROUNDING_PLACES)) + '/' + str(DMScore.DEATHS_TOTAL))
        print('Score: ' + str(round(self.score / divisor, ROUNDING_PLACES)) + '/' + str(SCORE_TOTAL) + '\n') 

    def __add__(self, other_score):
        self.damage_efficiency += other_score.damage_efficiency
        self.kill_death += other_score.kill_death
        self.round_diff += other_score.round_diff
        self.frags += other_score.frags
        self.damage += other_score.damage
        self.kill_participation += other_score.kill_participation
        self.heal_efficiency += other_score.heal_efficiency
        self.deaths += other_score.deaths
        self.score += other_score.score
        return self

    def calculate_score(self):
        self.damage_efficiency = self.calculate_damage_efficiency_score(DMScore.DE_MIN, DMScore.DE_MAX, DMScore.DE_TOTAL)
        self.kill_death = self.calculate_kd_score(DMScore.KD_MIN, DMScore.KD_MAX, DMScore.KD_TOTAL)
        self.round_diff = self.calculate_round_diff_score(DMScore.ROUND_DIFF_MIN, DMScore.ROUND_DIFF_MAX, DMScore.ROUND_DIFF_TOTAL)
        self.frags = self.calculate_frag_score(DMScore.FRAGS_MIN, DMScore.FRAGS_MAX, DMScore.FRAGS_TOTAL)
        self.damage = self.calculate_damage_score(DMScore.DAMAGE_MIN, DMScore.DAMAGE_MAX, DMScore.DAMAGE_TOTAL)
        self.kill_participation = self.calculate_kill_participation_score(DMScore.KP_MIN, DMScore.KP_MAX, DMScore.KP_TOTAL)
        self.deaths = self.calculate_death_score(DMScore.DEATHS_MIN, DMScore.DEATHS_MAX, DMScore.DEATHS_TOTAL)
        self.score = self.damage_efficiency + self.kill_death + self.deaths + self.round_diff + self.frags + self.damage + self.kill_participation
        self.heal_efficiency = self.calculate_heal_percent_effiency_score(self.log.get_players_med(self.player), self.score, DMScore.HE_MIN, DMScore.HE_MAX, DMScore.HE_TOTAL)
        self.score += self.heal_efficiency 
