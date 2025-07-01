

from datetime import datetime, timedelta, timezone
import sys
import flet as ft
import jwt
sys.path.append('c:/Users/yeiso/OneDrive/Escritorio/Proyecto/final_proyect')
from app.core.secretManager import SecretManager
from app.utils.logger import Logger
from app.core.login import LogicLogin
from app.modules.login.interfaces.viewLogin import ViewLogin
from app.utils.builder import Builder
#Clase para menjar la logica del inicio de secicon de la vista de login
class LogicViewLogin:

    def __init__(self,view: ViewLogin):
        self.view = view
        self.page = view.page
        self.log = Logger("app/logs/Login.log").get_logger()
        self.logicLogin = LogicLogin()
        self.secret = SecretManager().get_secretJWT()
        self.algorithm = "HS256"
    
    async def create_jwt(self,email:str,name:str) -> str:
        payload = {
            "email": email,
            "name" : name,
            "exp": datetime.now(timezone.utc)+ timedelta(minutes=30) 
        }

        token = jwt.encode(payload,self.secret,algorithm=self.algorithm)
        return token

    #Funcion que se va ejecutar apenas se le de clikc al boton de iniciar sesion
    async def iniciar_sesion(self,e) -> bool:
        try:
            #Primero triago los dos textfield de la vista de login
            usuario = self.view.refTexfieldUser.current.content.value
            contrasena = self.view.refTexfieldPassword.current.content.value

            #Verifico que los campos no esten vacios
            if not usuario or not contrasena:
                self.log.error("Los campos de usuario y contraseña no pueden estar vacíos.")
                return False
            
            #Verifico que el usuario y la contraseña sean correctos
            email, name = await self.logicLogin.loginUser(usuario, contrasena)
            if not email or not name:
                self.log.error("Usuario o contraseña incorrectos.")
                Builder().crearSnackBar(
                    e, 
                    "Usuario o contraseña incorrectos.", 
                    "error"
                )
                return False
            
            # Crear JWT
            jwt_token = await self.create_jwt(email, name)

            # Redirigir al tablero con el token
            e.page.go(f"/tableroPrincipal?token={jwt_token}")
        except Exception as ex:
            self.log.error(f"Error al iniciar sesión: {ex}")
            return False

