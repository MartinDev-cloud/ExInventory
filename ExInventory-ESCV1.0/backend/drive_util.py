import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Alcances
SCOPES = ['https://www.googleapis.com/auth/drive']

def autenticar_drive():
    creds = None

    # Ruta del token.json en la misma carpeta que este script
    script_dir = os.path.dirname(os.path.abspath(__file__))  # Carpeta donde está este script
    token_path = os.path.join(script_dir, 'token.json')
    credentials_path = os.path.join(script_dir, 'credentials.json')  # Ruta relativa

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
        creds = flow.run_local_server(port=0)
        with open(token_path, 'w') as token_file:
            token_file.write(creds.to_json())

    service = build('drive', 'v3', credentials=creds)
    return service

def subir_archivo(service, archivo_local, carpeta_id=None):
    nombre = os.path.basename(archivo_local)
    file_metadata = {'name': nombre}
    if carpeta_id:
        file_metadata['parents'] = [carpeta_id]
    media = MediaFileUpload(archivo_local, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return file.get('id')
