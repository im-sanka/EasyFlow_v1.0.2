from apps.security.streamlit_authenticator import authenticate as auth
import yaml
from apps.security.credentials import get_credentials
from apps.security.credentials import add_credentials_to_db
from yaml import SafeLoader

name, authentication_status, username, authenticator = None, None, None, None


def authenticate():
    global name, authentication_status, username, authenticator
    with open('apps/security/config.yaml') as auth_config_file:
        auth_config = yaml.load(auth_config_file, Loader=SafeLoader)
    credentials = get_credentials()
    authenticator = auth.Authenticate(
        credentials,
        auth_config['cookie']['name'],
        auth_config['cookie']['key'],
        auth_config['cookie']['expiry_days'],
        auth_config['preauthorized']
    )
    return authenticator.login('Login', 'sidebar')


def get_authenticator():
    if authenticator is not None and authenticator.__class__ == auth.Authenticate:
        return authenticator


def get_user_name():
    return name


def get_username():
    return username


def enable_logout():
    if authenticator is not None:
        authenticator.logout('Logout', 'sidebar')

def register_user():
    if authenticator is not None:
        add_credentials_to_db(authenticator.credentials)
