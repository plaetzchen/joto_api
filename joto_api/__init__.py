import requests
import time

ROOT_DOMAIN = "https://api.joto.io"
OAUTH_ENDPOINT = "https://those-apps.auth.eu-west-1.amazoncognito.com"

class JotoAPI:
    """
    The class representing the tools to interact with the Joto API

    Attributes:
        client_id (str): The client id used, usually given in the construction method
        client_secret (str): The client secret used to communicate with the server, usually given in the construction method
        token (str): The token used to communicate with the API, see get_token() method

    """

    client_id = None
    secret = None
    token = None

    def __init__(self,client_id,secret):
        """Init the JotoAPI client

        Use this __init__ method to set your client_id and client_secret

        Args:
            client_id (str): The client id provided by Joto
            client_secret (str): The client secret provided by Joto

        """

        self.client_id = client_id
        self.secret = secret

    def get_token(self):
        """Method to get a token for your given client id and secret

        Returns:
            The token after receiving it
        """

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
        """Send a JotObject to the server in order to start processing. The methods returns as soon as the server has processed the code and the Jot is ready to be sent
    
        Args:
            jot: The JotObject to send

        Returns:
            The stored and ready to draw objects or None if failed

        """

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
        """Get a jot from the server after sending it using the jot id

        Args:
            jot_id: The id of the jot to fetch

        Returns:
            The fetched jot from the service or None

        """

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
        """Send the jot to a given playlist

        Args:
            jot_id: The id of the jot after sending it to the API using create_jot()
            playlist_id: The id of the playlist to send it to, typically received from the calling Joto API

        Returns:
            True if sent successfully, False if not

        """

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
        """Wait for a jot to be ready, uses the fetch_jot() method

        Note:
            There is a 3 second wait between each retry

        Args:
            jot_id: The jot_id to check for readiness
            retries: How often the method should check before failing

        Returns:
            The jot if ready, None if it couldn't be processed in time

        """

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

    Attributes:
        title (str): The title of the jot, shows on the user interface after drawing
        description (str): The description of the Jot, also shows in the user interface to users
        svg (str): The svg content of the draw, needs to be valid SVG in order to be drawn successfully
        categories (list): A list of strings that represent the categories of the Jot (optional)
        tags (list): A list of strings that represent tags (optional)
        partMeta (dict): A dict with meta data (optional)
        meta (dict): A dict with meta data (optional)

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
        """Returns a dict represantation of the jot to be used when sent to server

        Returns:
            The dict of the JotObject to send to the server

        """
        return {"title":self.title,"description":self.description,"svg":self.svg,"categories":self.categories,"tags":self.tags,"partMeta":self.partMeta,"meta":self.meta}