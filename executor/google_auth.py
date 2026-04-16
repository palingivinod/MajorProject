from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
import config.settings as cfg
import os

def get_credentials():
    if os.path.exists(cfg.GOOGLE_TOKEN_PATH):
        return Credentials.from_authorized_user_file(
            cfg.GOOGLE_TOKEN_PATH, cfg.GOOGLE_SCOPES
        )

    flow = InstalledAppFlow.from_client_secrets_file(
        cfg.GOOGLE_CREDENTIALS_PATH,
        cfg.GOOGLE_SCOPES
    )

    creds = flow.run_local_server(port=0)

    with open(cfg.GOOGLE_TOKEN_PATH, "w") as token:
        token.write(creds.to_json())

    return creds
