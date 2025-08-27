# api/apps.py

import firebase_admin
import os
from django.apps import AppConfig
from django.conf import settings
from firebase_admin import credentials
from dotenv import load_dotenv

class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        # Carrega as variáveis de ambiente do .env
        BASE_DIR = settings.BASE_DIR
        load_dotenv(os.path.join(BASE_DIR, '.env'))

        # Pega o caminho para as credenciais do Firebase
        cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH")

        # Verifica se o app do Firebase já foi inicializado para evitar erros
        if not firebase_admin._apps:
            cred = credentials.Certificate(os.path.join(BASE_DIR, cred_path))
            database_url = os.getenv("FIREBASE_DATABASE_URL")
            firebase_admin.initialize_app(cred, {
                'databaseURL': database_url
            })

        print("🔥 Firebase Conectado!") 