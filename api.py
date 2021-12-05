import requests
import json

class LogList(object):

    def __init__(self, title=None, tfmap=None, uploader=None, player=None, limit=1000, offset=0):
        base_url = "http://logs.tf/api/v1/log?"
        title_parameter = "title=" + title + "&" if title != None else ""
        map_parameter = "map=" + tfmap + "&" if tfmap != None else ""
        uploader_parameter = "uploader=" + uploader + "&" if uploader != None else ""
        player_parameter = "player=" + player + "&" if player != None else ""
        limit_parameter = "limit=" + str(limit) + "&"
        offset_parameter = "offset=" + str(offset)
        url = base_url + title_parameter + map_parameter + uploader_parameter + player_parameter + limit_parameter + offset_parameter
        data = requests.get(url)
        self.__dict__ = data.json()
        
class Log(object):

    def __init__(self, log_id):
        self.base_url = "http://logs.tf/json/"
        url = self.base_url + str(log_id)
        data = requests.get(url)
        self.__dict__ = data.json()

    def get_scout_medic_combos(self):
        scout_medic_combos = dict()
        for medic in self.healspread:
            top_heal_scout = ''
            top_heal = 0
            for player in self.healspread[medic]:
                if self.healspread[medic][player] > top_heal and self.played_scout(player):
                    top_heal = self.healspread[medic][player]
                    top_heal_scout = player
            scout_medic_combos[top_heal_scout] = medic
        return scout_medic_combos

    def played_scout(self, player):
        if self.players[player]['class_stats'][0]['type'] == 'scout':
            return True
        else:
            return False    

class LogUploader(object):

    def __init__(self, title, tfmap, key, logfile=None, file_path=None, uploader="LogsTFAPIWrapper", updatelog=None):
        self.url = 'http://logs.tf/upload'
        file_to_upload = logfile
        if logfile == None and file_path != None:
            file_to_upload = open(file_path, 'rb').read()

        self.files = {'logfile': file_to_upload, 
                'title': title,
                'map': tfmap,
                'key': key,
                'uploader': uploader
                }
        if updatelog != None:
            files['updatelog'] = updatelog

    def upload_log(self):
        response = requests.post(self.url, files=self.files, data=self.files, verify=False)
        print(response.json()) 

def id_from_logs_url(url):
    url = url.replace('https://logs.tf/', '')
    url = url.replace('http://logs.tf/', '')
    if '#' in url:
        return url.split('#')[0]
    else:
        return url