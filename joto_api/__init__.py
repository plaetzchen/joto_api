import requests
import time

ROOT_DOMAIN = "https://api.joto.io"
OAUTH_ENDPOINT = "https://those-apps.auth.eu-west-1.amazoncognito.com"

class JotoAPI:
    """
    The class representing the tools to interact with the Joto API

    ...

    Attributes
    ----------
    client_id : str
        The client id used, usually given in the construction method
    client_secret : str
        The client secret used to communicate with the server, usually given in the construction method
    token : str
        The token used to communicate with the API, see get_token() method

    Methods
    -------
    get_token()
        A method to get an access token with the client id and secret. Handled automatically when using other methods
    create_jot(jot)
        Send a JotObject to the server in order to start processing. The methods returns as soon as the server has processed the code and the Jot is ready to be sent
    fetch_jot(jot_id)
        Used by wait_for_jot_ready(jot) to fetch the jot after creation to check for ready state
    send_jot_id_to_playlist(jot_id,playlist)
        Takes the jot_id after creating a jot and sends it to a given playlist id.
    wait_for_jot_ready(retries=5)
        Internal method to fetch a jot and check if GCODE is processed, will retry to get data every 3 seconds
    """

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
    """
    The class representing a Jot that is sent to the joto servers

    ...

    Attributes
    ----------
    title : str
        The title of the jot, shows on the user interface after drawing
    description : str
        The description of the Jot, also shows in the user interface to users
    svg : str
        The svg content of the draw, needs to be valid SVG in order to be drawn successfully
    categories : list
        A list of strings that represent the categories of the Jot (optional)
    tags : list
        A list of strings that represent tags (optional)
    partMeta: dict
        A dict with meta data (optional)
    meta: dict
        A dict with meta data (optional)

    Methods
    -------
    to_dict()
        Returns a dict represantation of the jot to be used when sent to server
    """

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