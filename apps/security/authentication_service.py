from apps.security.streamlit_authenticator import authenticate as auth
import yaml
from yaml import SafeLoader

name, authentication_status, username, authenticator = None, None, None, None


def authenticate():
    global name, authentication_status, username, authenticator
    with open('apps/security/config.yaml') as auth_config_file:
        auth_config = yaml.load(auth_config_file, Loader=SafeLoader)

    authenticator = auth.Authenticate(
        auth_config['credentials'],
        auth_config['cookie']['name'],
        auth_config['cookie']['key'],
        auth_config['cookie']['expiry_days'],
        auth_config['preauthorized']
    )
    name, authentication_status, username = authenticator.login('Login', 'main')


def get_auth_status():
    return authentication_status


def get_authenticator():
    if authenticator is not None and authenticator.__class__ == auth.Authenticate:
        return authenticator


def get_user_name():
    return name


def get_username():
    return username


def enable_logout():
    authenticator.logout('Logout', 'sidebar')
