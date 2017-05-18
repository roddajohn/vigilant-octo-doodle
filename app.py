from flask import url_for, request, session, redirect, Flask # Necessary flask imports

from oauth2client.client import flow_from_clientsecrets, OAuth2Credentials # OAuth library, import the function and class that this uses

from httplib2 import Http # The http library to issue REST calls to the oauth api

import json # Json library to handle replies

app = Flask(__name__) # Create flask object

app.config.update(dict( # Make sure the secret key is set for use of the session variable
    SECRET_KEY = 'secret'
    ))

@app.route('/auth/oauth_testing', methods = ['POST', 'GET']) # OAuth authentication route
def oauth_testing():
    flow = flow_from_clientsecrets('client_secrets.json',
                                   scope = 'https://www.googleapis.com/auth/userinfo.email',
                                   redirect_uri = url_for('oauth_testing', _external = True))
    """
    The flow object will handle the authentication flow, it is two step authentication
    The first argument is the json file that contains secret keys and the like, included in this repo is a sample
    You will have to aquire these keys and put together this file yourself--this is well documented online
    The scope is the amount of permissions you which to use, I am just using a basic scope for getting user information (including email)
    The redirect uri is where the use will be spit to after logging in, I just use the same route (the _external flag generates a non relative url)
    """

    if 'code' not in request.args: # If we are on the first step of the authentication
        auth_uri = flow.step1_get_authorize_url() # This is the url for the nice google login page
        return redirect(auth_uri) # Redirects to that page
    else: # That login page will redirect to this page but with a code in the request arguments
        auth_code = request.args.get('code')
        credentials = flow.step2_exchange(auth_code) # This is step two authentication to get the code and store the credentials in a credentials object
        session['credentials'] = credentials.to_json() # Converts the credentials to json and stores it in the session variable
        return redirect(url_for('sample_info_route'))

@app.route('/auth/sample_info_route', methods = ['POST', 'GET'])
def sample_info_route():
    if 'credentials' not in session: # If the credentials are not here, user must login
        return redirect(url_for('oauth_testing'))

    credentials = OAuth2Credentials.from_json(session['credentials']) # Loads the credentials from the session
    
    if credentials.access_token_expired: # If the credentials have expired, login
        return redirect(url_for('oauth_testing'))
    else:
        http_auth = credentials.authorize(Http()) # This will authorize this http_auth object to make authenticated calls to an oauth api

        response, content = http_auth.request('https://www.googleapis.com/oauth2/v1/userinfo?alt=json') # Issues a request to the google oauth api to get user information
        
        c = json.loads(content) # Load the response

        return c['email'] # Return the email

app.run(debug = True) # Runs the app
