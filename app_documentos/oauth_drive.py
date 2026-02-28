import os
import pickle

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLIENT_SECRET_FILE = os.path.join(BASE_DIR, 'credenciales', 'oauth.json')
TOKEN_FILE = os.path.join(BASE_DIR, 'credenciales', 'token.pickle')

SCOPES = ['https://www.googleapis.com/auth/drive.file']


def get_drive_service_oauth():
    creds = None

    # 🔹 Si ya existe token guardado, lo usamos
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)

    # 🔹 Si no hay credenciales válidas, pedimos login solo una vez
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRET_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0)

        # 🔹 Guardamos token para futuros usos
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)
    return service