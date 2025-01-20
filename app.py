from flask import Flask, request, redirect, url_for, render_template, flash, session
from Firebase import verify_token  # Importamos la función de firebase.py
from firebase_admin import firestore
from firebase_admin import auth  # Importamos el SDK de Firebase aquí
import os
import requests
import base64
import hashlib

import json


# Paso 1: Generar el 'code_verifier' (aleatorio)
code_verifier = base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8').rstrip("=")

# Paso 2: Generar el 'code_challenge' (SHA256 del code_verifier)
code_challenge = base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode('utf-8')).digest()).decode('utf-8').rstrip("=")

# FITBIT COSAS 
fitbit_client_id ='23PYCZ'
fitbit_client_secret = 'db9f844ee0d452081f238f04fe0a6d57'
redirect_uri = 'http://127.0.0.1:5000/homefitbit'
scope = 'activity heartrate location nutrition oxygen_saturation profile respiratory_rate settings sleep social temperature weight'



app = Flask(__name__)
app.secret_key = 'una_clave_aleatoria_y_segura'  

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
          
            id_token = request.form['idToken']  
            print(id_token)

            decoded_token = verify_token(id_token) 
            print(decoded_token)
            if decoded_token:
             session['user_data'] = decoded_token  # Almacena en la sesión

             return redirect(url_for('fitbitloginscreen'))  # Redirigir al login después del registro

            else:
                return "Token inválido", 401

        except Exception as e:
            return f"Error: {str(e)}", 401
    return render_template('login.html')  

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            # Crear usuario con Firebase Authentication
            user = auth.create_user(
                email=email,
                password=password
            )

            # Guardar información adicional en Firestore (opcional)
            db = firestore.client()
            user_ref = db.collection('users').document(user.uid)
            user_ref.set({
                'email': user.email,
                'createdAt': firestore.SERVER_TIMESTAMP
            })

            flash('Usuario registrado exitosamente!', 'success')
            return redirect(url_for('login'))  # Redirigir al login después del registro

        except Exception as e:
            flash(f'Error al registrar usuario: {str(e)}', 'error')
            return redirect(url_for('login'))  # Redirigir al formulario de registro si hay error

    return render_template('register.html')  # Mostrar el formulario de registro


@app.route('/fitbitoauth', methods=['GET'])
def fitbitoauth():

    #URL CON LOS DATOS DE FITBIT Y TODO ESO
    authorization_url = f"https://www.fitbit.com/oauth2/authorize?&client_id={fitbit_client_id}&response_type=code&code_challenge={code_challenge}&code_challenge_method=S256&scope={scope}"

    # Redirige a la URL de Fitbit para que el usuario inicie sesión
    return redirect(authorization_url)
    

@app.route('/fitbitloginscreen', methods=['GET', 'POST'])
def fitbitloginscreen():
    
    return render_template('fitbitloginscreen.html')







#LOGICA DE TOKENS DE FITBIT!!!


def obtain_tokens(authorization_code):
    if not authorization_code:
        return "No se pudo obtener el código de autorización.", 400

    token_url = "https://api.fitbit.com/oauth2/token"
    client_credentials = f"{fitbit_client_id}:{fitbit_client_secret}"
    encoded_credentials = base64.b64encode(client_credentials.encode('utf-8')).decode('utf-8')

    headers = {
        'Authorization': f"Basic {encoded_credentials}",
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    data = {
        'client_id': fitbit_client_id,
        'code': authorization_code,
        'code_verifier': code_verifier,
        'grant_type': 'authorization_code',

    }

    # Realizar la solicitud POST al endpoint de tokens
    response = requests.post(token_url, headers=headers, data=data)

    if response.status_code == 200:
        tokens = response.json()  # Aquí obtienes los tokens como diccionario
        return tokens
    else:
        return f"Error al obtener tokens: {response.status_code}<br>{response.text}", 400
    




@app.route('/homefitbit', methods=['GET'])
def homefitbit():
    # Aquí recibirías el código de autorización de Fitbit después de redirigir
    code = request.args.get('code')
    
    if not code:
        return "Código de autorización no recibido", 400
    

    user_data = session.get('user_data')
    user_id = user_data.get('user_id')
    


    #funcion para llamar el oauth endopint de fitbit y obtener los tokens y el id del user de fitbit
    access_token = obtain_tokens(code)

    #metodo para guardar esos datos de tokens en firestore
    save_tokens_to_firestore(user_id,access_token)
    print(" --------")
    print(access_token)
    # Luego de obtener el token de acceso, podrías almacenarlo y hacer cualquier otra acción.
    flash('Login con Fitbit exitoso!', 'success')
    return render_template('loggedin.html')





def save_tokens_to_firestore(user_id, tokens):
    print(f"tokens: {tokens}")
    print(f"Tipo de tokens: {type(tokens)}")

    db = firestore.client()

    fitbit_collection = db.collection('fitbit_users')

    # Crea o actualiza el documento del usuario
    fitbit_doc = fitbit_collection.document(user_id)
    
   
    # Datos a guardar
    data = {
        'access_token': tokens['access_token'],
        'refresh_token': tokens['refresh_token'],
        'expires_in': tokens['expires_in'],  # Tiempo de vida en segundos
        'scopes': tokens.get('scope', '').split(' '),  # Lista de scopes autorizados
        'token_type': tokens['token_type'],
        'user_id': tokens['user_id']
    }

    # Guarda o actualiza los datos en Firestore
    fitbit_doc.set(data)
    print(f"Datos guardados exitosamente en Firestore para el usuario {user_id}")







if __name__ == '__main__':
    app.run(debug=True)



#FUNCIONES DE FITBIT

