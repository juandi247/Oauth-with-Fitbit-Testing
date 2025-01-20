import os
from requests_oauthlib import OAuth2Session
from requests.auth import HTTPBasicAuth

# Aquí colocas las credenciales de Fitbit
FITBIT_CLIENT_ID = 'tu_client_id'
FITBIT_CLIENT_SECRET = 'tu_client_secret'
FITBIT_REDIRECT_URI = 'tu_redirect_uri'

# URL para la autorización y el token de Fitbit
FITBIT_AUTHORIZATION_URL = 'https://www.fitbit.com/oauth2/authorize'
FITBIT_TOKEN_URL = 'https://api.fitbit.com/oauth2/token'

# Crea un cliente OAuth2 para Fitbit
def get_fitbit_oauth_session():
    oauth = OAuth2Session(FITBIT_CLIENT_ID, redirect_uri=FITBIT_REDIRECT_URI)
    authorization_url, state = oauth.authorization_url(FITBIT_AUTHORIZATION_URL)
    return oauth, authorization_url

# Intercambia el código de autorización por el token
def get_access_token(oauth, authorization_response):
    token = oauth.fetch_token(FITBIT_TOKEN_URL, authorization_response=authorization_response,
                              client_secret=FITBIT_CLIENT_SECRET, auth=HTTPBasicAuth(FITBIT_CLIENT_ID, FITBIT_CLIENT_SECRET))
    return token
