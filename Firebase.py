
import firebase_admin
from firebase_admin import credentials, auth

# Inicializa la aplicación de Firebase con la credencial del archivo JSON
cred = credentials.Certificate("firebase.json")
firebase_admin.initialize_app(cred)

# Función para verificar un token
def verify_token(id_token):
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        return None
