
import asyncio
from datetime import datetime, timedelta, timezone
from urllib.parse import quote
from fastapi import APIRouter,Request
from authlib.integrations.starlette_client import OAuth
import sys

from fastapi.responses import JSONResponse, RedirectResponse
import jwt 
sys.path.append('c:/Users/yeiso/OneDrive/Escritorio/Proyecto/final_proyect')
from app.utils.logger import Logger
from app.core.login import LogicLogin
from app.core.secretManager import SecretManager

#Clase para manejar las rutas de la api
class RouterApiCognito:

    def __init__(self):
        self.loginLogic = LogicLogin()
        self.router = APIRouter()
        self.log = Logger("app/logs/apiMain.log").get_logger()
        self.secret = SecretManager().get_secretJWT()
        self.algorithm = "HS256"
        self.router.get(
            "/login", 
            summary="Para hacer login con Google por medio de Cognito",
            tags=["Cognito"])(self.login)
        self.router.get(
            "/callback", 
            summary="Recibe el token de Cognito y redirige al frontend Flet",
            tags=["Cognito"])(self.callback)
        self.router.get(
            "/logout", 
            summary="Para hacer logout de Cognito",
            tags=["Cognito"])(self.logout)
        self.oauth = OAuth()
        self.oauth.register(
                    name='cognito',
                    client_id="10kvfjgif2sbhsqq3f742j78f2",
                    client_secret="j1mmg6uljs77vvs85h2j20qlugd4p65ib9n0pdh29d6qfojl5rt",
                    server_metadata_url="https://cognito-idp.us-east-1.amazonaws.com/us-east-1_67cQeZ8tk/.well-known/openid-configuration",
                    client_kwargs={
                        'scope': 'openid email phone'
                    }
                )
    async def create_jwt(self,email:str,name:str) -> str:
        payload = {
            "email": email,
            "name" : name,
            "exp": datetime.now(timezone.utc)+ timedelta(minutes=30) 
        }

        token = jwt.encode(payload,self.secret,algorithm=self.algorithm)
        return token

    async def login(self, request: Request):
        try:
            redirect_uri = "http://localhost:8000/cognito/callback"
            return await self.oauth.cognito.authorize_redirect(request, redirect_uri)
        except Exception as ex:
            self.log.error(f"Error en el login de Cognito: {ex}")
            return JSONResponse(
                {"error": "Error al generar URL de login"},
                status_code=500
            )

    # ✅ Paso 2: Recibir token y redirigir al Flet Frontend
    async def callback(self,request: Request):
        try:
            token = await self.oauth.cognito.authorize_access_token(request)
            user = token.get("userinfo")

            # Verificar si hay user si no hay redirigir a error
            if not user:
                return RedirectResponse("http://localhost:52928/error")

            # Puedes extraer más datos si quieres
            email = user.get("email")
            name = user.get("name") or user.get("cognito:username") or "Usuario"

            if not await self.loginLogic.verify_userGoogle(email):
                # Construir URL de logout
                logout_url = (
                    "https://us-east-167cqez8tk.auth.us-east-1.amazoncognito.com/logout"
                    "?client_id=10kvfjgif2sbhsqq3f742j78f2"
                    "&logout_uri=http://localhost:52928"
                )
                return RedirectResponse(logout_url)

            # Crear JWT
            jwt_token = await self.create_jwt(email, name)
            self.log.info(f"JWT Token: {jwt_token}")

            # Redirigir al frontend Flet con el JWT
            redirect_url = f"http://localhost:52928/tableroPrincipal?token={quote(jwt_token)}"
            self.log.info(f"Redirigiendo a: {redirect_url}")    
            return RedirectResponse(redirect_url)

        except Exception as ex:
            self.log.error(f"Error en el callback de Cognito: {ex}")
            return RedirectResponse("http://localhost:52928/error")

    async def logout(self):
        try:
            logout_url=(
                "https://us-east-167cqez8tk.auth.us-east-1.amazoncognito.com/logout"
                "?client_id=10kvfjgif2sbhsqq3f742j78f2"
                "&logout_uri=http://localhost:52928"
            )
            return RedirectResponse(logout_url)
        except Exception as ex:
            self.log.error(f"Error en el logout de Cognito: {ex}")
            return RedirectResponse("http://localhost:52928/error")
        