import asyncio
import sys
import time
import flet as ft
from urllib.parse import urlparse, parse_qs
from jwt import InvalidTokenError
sys.path.append('c:/Users/yeiso/OneDrive/Escritorio/Proyecto/final_proyect')
from app.utils.jwtValidator import JWTValidator
from app.utils.sessionManager import SessionManager
from app.modules.login.build.responsi import ResponsiLogin

#Clase para manejar las rutas del frontend de Flet
class FletFrontendRouter:
    def __init__(self, page: ft.Page,view,tablero):
        self.page = page
        self.view = view
        self.tablero = tablero

    def aplicar_respondiHome(self):
        height = self.page.height
        responsi = ResponsiLogin(self.view)
        responsi.update_height(height)

    def handle(self):
        route = self.page.route
        self.page.views.clear()
        self.page.update()
        if route.startswith("/tableroPrincipal"):
            parsed = urlparse(route)
            query_params = parse_qs(parsed.query)
            token = query_params.get("token", [""])[0]

            try:
                email, name = JWTValidator().get_user_info(token)
                SessionManager.set_user(self.page, email, name)
                self.page.go("/tablero")
                return
            except InvalidTokenError:
                self.page.go("/error")
                return
        elif route == "/tablero":
            if not SessionManager.is_user_logged_in(self.page):
                self.page.go("/")
                return
            email, name = SessionManager.get_user(self.page)
            self.page.views.append(self.tablero.create_tablero())
            self.page.update()

        elif route == "/":
            self.page.views.append(self.view.create_login())
            SessionManager.clear_user(self.page)
            self.page.update()
            self.aplicar_respondiHome()

        self.page.update()