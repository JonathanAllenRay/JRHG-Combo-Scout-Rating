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
