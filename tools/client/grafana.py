import requests
import json

get_db_api = "/api/dashboards/uid/"

class client:
    auth = ""
    server = ""
    
    def __init__(self, server, auth):
        self.server = server
        self.auth = auth
        
    # fetch dashboard json from grafana api
    def get_db(self, db_id):
        get_db_url = f"http://{self.auth}{self.server}{get_db_api}{db_id}"
        return json.loads(requests.get(get_db_url).text)["dashboard"]