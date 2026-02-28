from google.oauth2 import service_account
from googleapiclient.discovery import build
import os

# Ruta del JSON de credenciales
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, 'credenciales', 'drive.json')

SCOPES = ['https://www.googleapis.com/auth/drive']

def get_drive_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES,
        subject="imagenb129@gmail.com"   # 👈 TU CORREO REAL
    )
    service = build('drive', 'v3', credentials=creds)
    return service


def subir_archivo_drive(ruta_archivo, nombre_archivo, folder_id=None):
    service = get_drive_service()

    from googleapiclient.http import MediaFileUpload

    file_metadata = {
        'name': nombre_archivo
    }

    if folder_id:
        file_metadata['parents'] = [folder_id]

    media = MediaFileUpload(ruta_archivo, resumable=True)

    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    return file.get('id')