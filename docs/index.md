# joto_api
A python package to interact with the Playlist API of Joto - The robotic drawing board. 

Usage
---
Currently you will need to interact with the Joto Team to gain access to a client id and secret. After you have this you should create a project that is hosted on a service like Google Cloud Functions, AWS Lambda or another server of your choice. The URL to call your function also needs to be sent to your contact at Joto.

How it works:
* A user adds your app to their playlist
* The Joto service calls your endpoint with a payload, including the playlist id of the user and the meta data of the call
* You generate a SVG baded on the meta data
* You create a JotObject with this package
* After creating the JotObject you sent it's id to the playlist
* Your user' Joto starts drawing

Example
---

```
import joto_api

# Assuming a incoming flask request
def handle_request(request):
    if request.method == 'POST':
        request_json = request.get_json(force=True)
        
        svg = '<svg version="1.1" xmlns="http://www.w3.org/2000/svg" width="500" height="500"></svg>'

        client_id = "YOUR_ID"
        client_secret = "YOUR_SECRET"

        # Getting the playlist id from the request
        playlist_id = request_json["playlistId"]
        
        # Creating the JotoAPI instance to handle communication
        joto = joto_api.JotoAPI(client_id,client_secret)
        
        # Creating a JotObject to send
        jotObject = joto_api.JotObject("Test","Test",svg)
        
        # Create the jot on the server and wait for processing
        jot = joto.create_jot(jotObject)
        
        if jot:
            # Add the jot id to the playlist you got in your request
            sent = joto.send_jot_id_to_playlist(jot["jotId"],playlist_id)
        else:
            return abort(500)
        if sent:
            return "Sent"
        else:
            return abort (500)
    else:
        return abort(405)
```
