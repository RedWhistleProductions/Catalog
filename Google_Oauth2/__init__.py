from flask import Blueprint, request, redirect, make_response
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError

import httplib2, json, requests


def init(app=None, Flask_Session = None, Client_Secret='client_secrets.json'):
    Google_Oauth2 = Blueprint('Google_Oauth2', __name__)
    DATA_CLIENT_ID = json.loads(open(Client_Secret, 'r').read())['web']['client_id']

    @Google_Oauth2.route('/gconnect', methods=['POST'])
    def gconnect():
        # Validate state token
        if request.args.get('state') != Flask_Session['state']:
            response = make_response(json.dumps('Invalid state parameter.'), 401)
            response.headers['Content-Type'] = 'application/json'
            return response
        # Obtain authorization code
        code = request.data

        try:
            # Upgrade the authorization code into a credentials object
            oauth_flow = flow_from_clientsecrets(Client_Secret, scope='')
            oauth_flow.redirect_uri = 'postmessage'
            credentials = oauth_flow.step2_exchange(code)
        except FlowExchangeError:
            response = make_response(
                json.dumps('Failed to upgrade the authorization code.'), 401)
            response.headers['Content-Type'] = 'application/json'
            return response

        # Check that the access token is valid.
        access_token = credentials.access_token
        url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
               % access_token)
        h = httplib2.Http()
        result = json.loads(h.request(url, 'GET')[1])
        # If there was an error in the access token info, abort.
        if result.get('error') is not None:
            response = make_response(json.dumps(result.get('error')), 500)
            response.headers['Content-Type'] = 'application/json'
            return response

        # Verify that the access token is used for the intended user.
        gplus_id = credentials.id_token['sub']
        if result['user_id'] != gplus_id:
            response = make_response(
                json.dumps("Token's user ID doesn't match given user ID."), 401)
            response.headers['Content-Type'] = 'application/json'
            return response

        # Verify that the access token is valid for this app.
        if result['issued_to'] != DATA_CLIENT_ID:
            response = make_response(
                json.dumps("Token's client ID does not match app's."), 401)
            print("Token's client ID does not match app's.")
            response.headers['Content-Type'] = 'application/json'
            return response

        stored_access_token = Flask_Session.get('access_token')
        stored_gplus_id = Flask_Session.get('gplus_id')
        if stored_access_token is not None and gplus_id == stored_gplus_id:
            response = make_response(json.dumps('Current user is already connected.'),
                                     200)
            response.headers['Content-Type'] = 'application/json'
            return response

        # Store the access token in the session for later use.
        Flask_Session['access_token'] = credentials.access_token
        Flask_Session['gplus_id'] = gplus_id

        # Get user info
        userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
        params = {'access_token': credentials.access_token, 'alt': 'json'}
        answer = requests.get(userinfo_url, params=params)

        data = answer.json()

        Flask_Session['User_Name'] = data['name']
        Flask_Session['Picture'] = data['picture']
        Flask_Session['Email'] = data['email']
        name_array = Flask_Session['User_Name'].split()
        Flask_Session['First'] = name_array[0]
        Flask_Session['Last'] = name_array[1]

        return "Conected"

    # DISCONNECT - Revoke a current user's token and reset their Flask_Session

    @Google_Oauth2.route('/gdisconnect')
    def gdisconnect():
        access_token = Flask_Session.get('access_token')
        if access_token is None:
            return redirect("/Login")

        url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % Flask_Session['access_token']
        h = httplib2.Http()
        result = h.request(url, 'GET')[0]

        del Flask_Session['access_token']
        del Flask_Session['gplus_id']
        del Flask_Session['username']
        del Flask_Session['email']
        del Flask_Session['picture']
        return redirect("/Login")

    app.register_blueprint(Google_Oauth2)
