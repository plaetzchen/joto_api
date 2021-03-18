import requests
import time

ROOT_DOMAIN = "https://api.joto.io"
OAUTH_ENDPOINT = "https://those-apps.auth.eu-west-1.amazoncognito.com"

class JotoAPI:
    client_id = None
    secret = None
    token = None
    def __init__(self,client_id,secret):
        self.client_id = client_id
        self.secret = secret

    def get_token(self):
        if self.token == None:
            url = "{0}/oauth2/token".format(OAUTH_ENDPOINT)
            payload = {"grant_type":"client_credentials","scope":"","client_id":self.client_id,"client_secret":self.secret}
            token_request = requests.post(url,data=payload)
            token_json = token_request.json()
            self.token = token_json["access_token"]
            return self.token
        else:
            return self.token

    def create_jot(self,jot):
        token = self.get_token()
        url = "{0}/developer-jot/".format(ROOT_DOMAIN)
        payload = jot.to_dict()
        headers = {"Authorization":"Bearer {0}".format(token)}
        create_request = requests.post(url,json=payload,headers=headers)
        if create_request.status_code == requests.codes.ok:
            create_json = create_request.json()
            jot_id = create_json["jotId"]
            fetch_data = self.wait_for_jot_ready(jot_id)
            return fetch_data
        else:
            self.token = None
            print("Request failed",create_request.status_code)
            return None

    def fetch_jot(self,jot_id):
        token = self.get_token()
        url = "{0}/developer-jot/{1}".format(ROOT_DOMAIN,jot_id)
        headers = {"Authorization":"Bearer {0}".format(token)}
        fetch_request = requests.get(url,headers=headers)
        if fetch_request.status_code == requests.codes.ok:
            fetch_json = fetch_request.json()
            return fetch_json
        else:
            self.token = None
            print("Request failed",create_request.status_code)
            return None

    def send_jot_id_to_playlist(self,jot_id,playlist_id):
        token = self.get_token()
        url = "{0}/developer-jot/playlist/{1}".format(ROOT_DOMAIN,playlist_id)
        payload = {"jotId": "{0}".format(jot_id)}
        headers = {"Authorization":"Bearer {0}".format(token)}
        create_request = requests.post(url,json=payload,headers=headers)
        if create_request.status_code  == requests.codes.ok:
            return True
        else:
            self.token = None
            print("Request failed: ",create_request.status_code)
            return False

    def wait_for_jot_ready(self,jot_id,retries=5):
        for i in range(retries):
            jot = self.fetch_jot(jot_id)
            if jot["ready"] == True:
                return jot
            time.sleep(3)
        else:
            return None

class JotObject:
    def __init__(self,title,description,svg,categories=[],tags=[],partMeta={},meta={}):
        self.title = title
        self.description = description
        self.svg = svg
        self.categories = categories
        self.tags = tags
        self.partMeta = partMeta
        self.meta = meta

    def to_dict(self):
        return {"title":self.title,"description":self.description,"svg":self.svg,"categories":self.categories,"tags":self.tags,"partMeta":self.partMeta,"meta":self.meta}