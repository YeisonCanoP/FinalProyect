import asyncio
import sys
from typing import Union

import jwt
sys.path.append('c:/Users/yeiso/OneDrive/Escritorio/Proyecto/final_proyect')
from app.utils.logger import Logger
import boto3
from app.utils.utils import Utils
from app.utils.jwtValidator import JWTValidator

#Clase para manejar la logica de la vista de login 
class LogicLogin:

    def __init__(self):
        self.poolid = "us-east-1_67cQeZ8tk"
        self.log = Logger("app/logs/Login.log").get_logger()
        self.url = "http://localhost:8000/cognito/login"
        self.urlCierre = "http://localhost:8000/cognito/logout"
    
    #Funcion para iniciar con google
    async def login_google(self,e):
        e.page.launch_url(self.url,web_window_name="_self")

    #Funcion para cerrar sesion
    async def logout(self, e):
        e.page.launch_url(self.urlCierre, web_window_name="_self")
        
    async def verify_userGoogle(self,email: str) -> bool:
        try:
            if not email:
                self.log.error("El email proporcionado es vacío.")
                return False

            email.strip()  # Eliminar espacios en blanco al inicio y al final
    
            user_pool_id = self.poolid
            grupo_permitido = 'userValidate'

            cognito = boto3.client('cognito-idp', region_name='us-east-1')

            # 1. Buscar usuario por email
            res = cognito.list_users(
                UserPoolId=user_pool_id,
                Filter=f'email = "{email}"'
            )

            if not res['Users']:
                self.log.error(f"Usuario {email} no encontrado en el User Pool.")
                return False

            username = res['Users'][0]['Username']

            # 2. Verificar a qué grupos pertenece
            grupos = cognito.admin_list_groups_for_user(
                UserPoolId=user_pool_id,
                Username=username
            )

            nombres_grupos = [g["GroupName"] for g in grupos.get("Groups", [])]

            if grupo_permitido in nombres_grupos:
                return True
            else:
                self.log.error(f"Usuario {email} no pertenece al grupo permitido: {grupo_permitido}.")
                return False
        except Exception as ex:
            self.log.error(f"Error al verificar usuario {email}: {ex}")
            return False

    #Verificar si el usuario esta en el grupo permitido
    async def loginUser(self, usernama: str, password: str) -> Union[dict, bool]:
        try:
            if not usernama or not password:
                self.log.error("El nombre de usuario o la contraseña son vacíos.")
                return False

            secret_hash = Utils.get_secret_hash(usernama, '10kvfjgif2sbhsqq3f742j78f2', 'j1mmg6uljs77vvs85h2j20qlugd4p65ib9n0pdh29d6qfojl5rt')

            client = boto3.client('cognito-idp', region_name='us-east-1')
            response = client.initiate_auth(
                ClientId='10kvfjgif2sbhsqq3f742j78f2',
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': usernama,
                    'PASSWORD': password,
                    'SECRET_HASH': secret_hash
                },
            )
            if "AuthenticationResult" in response:
                id_token = response["AuthenticationResult"]["IdToken"]

                decode_token = jwt.decode(id_token, options={"verify_signature": False})
                email = decode_token.get("email")
                name = decode_token.get("name") or decode_token.get("cognito:username") or "Usuario"

                return {
                    "email": email,
                    "name": name
                }

            else:
                self.log.error(f"Error de autenticación para el usuario {usernama}. Respuesta: {response}")
                return False,False

        except Exception as ex:
            self.log.error(f"Credenciales incorrectas: {ex}")
            return False,False
    
    #Funcion para crear 3 ususarios por defecto y no tener que cambiarle la contraseña
    async def create_default_users(self):
        try:
            client = boto3.client('cognito-idp', region_name='us-east-1')
            users = [
                {"username": "admin", "password": "CosmoCano1234@"},
                {"username": "frank", "password": "Frank1234@"},
                {"username": "andres", "password": "Andres1234@"}
            ]

            for user in users:
                try:
                    client.admin_create_user(
                        UserPoolId=self.poolid,
                        Username=user["username"],
                        TemporaryPassword=user["password"],
                        UserAttributes=[
                            {'Name': 'email', 'Value': f'{user["username"]}@example.com'},
                            {'Name': 'email_verified', 'Value': 'true'}
                        ],
                        MessageAction='SUPPRESS' 
                    )
                    self.log.info(f"Usuario {user['username']} creado exitosamente.")
                    # Establecer la contraseña como permanente
                    client.admin_set_user_password(
                        UserPoolId=self.poolid,
                        Username=user["username"],
                        Password=user["password"],
                        Permanent=True
                    )
                except Exception as ex:
                    self.log.error(f"Error al crear usuario {user['username']}: {ex}")
        except Exception as ex:
            self.log.error(f"Error al crear usuarios por defecto: {ex}")