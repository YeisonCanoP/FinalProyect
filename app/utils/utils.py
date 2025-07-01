
import base64
from decimal import Decimal
import hashlib
import hmac
import flet as ft
import sys
sys.path.append('c:/Users/yeiso/OneDrive/Escritorio/Proyecto/final_proyect')
from app.utils.logger import Logger


#Clase para mannejar la creacion de funcines que se van ampoder eutilar en otro lado
class Utils:

    def __init__(self):
        self.log = Logger("app/logs/utils.log").get_logger()
        self.colorLetra = "#0D0630"
        self.fondo = "#f5f5f5"
    
    #Funcion para crear un hover 
    def on_hover(self,e,scale:int = 1.1,colorOrginal:str=None,colorCambiar:str=None,letras=None) -> None:
        button = e.control

        if not colorOrginal:
            if e.data == "true":
                button.scale = scale
            else:
                button.scale = 1.0
        
        else:
            
            if e.data == "true":
                button.scale = scale
                button.bgcolor = colorCambiar
                for letra in letras:
                    letra.current.color = ft.Colors.WHITE
            else:
                button.scale = 1.0
                button.bgcolor = colorOrginal
                for letra in letras:
                    letra.current.color = self.colorLetra
        
        button.update()
    
    #Funcion para crear el hash
    def get_secret_hash(username: str, client_id: str, client_secret: str) -> str:
        message = username + client_id
        dig = hmac.new(
            client_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).digest()
        return base64.b64encode(dig).decode()

    #Función para dar formato a un número (separadores de miles y decimales)
    def formatNumero(self,numero):
        # Convertir Decimal a float si es necesario
        if isinstance(numero, Decimal):
            numero = float(numero)

        if numero is None:
            return "0"
        # Formatear con separadores de miles (,) y dos decimales
        formateado = f"{numero:,.2f}"

        # Reemplazar separadores de miles y decimales al formato colombiano
        formateado = formateado.replace(",", "X").replace(".", ",").replace("X", ".")

        # Si termina en ",00", quitar los decimales
        if formateado.endswith(",00"):
            return formateado[:-3]

        return formateado