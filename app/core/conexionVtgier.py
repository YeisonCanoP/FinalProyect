import hashlib
import requests
import httpx
import json
import sys
sys.path.append("C:/Users/yeiso/OneDrive/Escritorio/ChatBot-Frank") 
from app.utils.logger import Logger
from app.core.secretManager import SecretManager
from app.utils.singleton import SingletonMeta

#Clase para manejar la conexión a Vtiger CRM
class ConexionVtiger(metaclass=SingletonMeta):

    def __init__(self):
        self.log = Logger("app/logs/ConexionVtiger.log").get_logger()
        self.datos_config = self.get_config()
        self.url = self.datos_config.get("apiEndpoint", "http://localhost:8080")
        self.username = self.datos_config.get("username", "admin")
        self.access_key = SecretManager().get_secretVtiger()
        self.session = None
        self.headers = {
            "User-Agent": "Mozilla/5.0"
        }

    #Funcion para traer los datos de config para la configruacion de la conexión
    def get_config(self):
        try:
            with open("app/config/config.json", "r", encoding="utf-8") as file:
                    config = json.load(file)
                    return config.get("config", {})
        except FileNotFoundError:
            self.log.error("Archivo de configuración no encontrado.")
        except json.JSONDecodeError:
            self.log.error("Error al decodificar el archivo de configuración JSON.")
        except Exception as ex:
            self.log.error(f"Error inesperado al cargar la configuración: {ex}")

    #Funcion para iniciar sesión en Vtiger CRM
    async def login(self) -> None:
        try:
            async with httpx.AsyncClient() as client:
                #Hago la respuesat para comenzar el inicio de sesión
                response = await client.get(f"{self.url}/webservice.php?operation=getchallenge&username={self.username}",headers=self.headers)
                if response.status_code != 200:
                    self.log.error(f"Error al obtener el challenge de Vtiger: {response.status_code} - {response.text}")
                    self.session = None
                    return
                
                try:
                    challenge_token = response.json()['result']['token']
                except KeyError:
                    self.log.error("Error al obtener el token del challenge. Respuesta inesperada de Vtiger.")
                    self.session = None
                    return

                #Calculo el hash MD5 de la combinación del token y la clave de acceso
                to_hash = challenge_token + self.access_key
                md5_hash = hashlib.md5(to_hash.encode()).hexdigest()

                #login con md5_hash
                login_params = {
                    "operation": "login",
                    "username": self.username,
                    "accessKey": md5_hash
                }
                login_response = await client.post(f"{self.url}/webservice.php", data=login_params,headers=self.headers)
                result = login_response.json()
                if result["success"]:
                    datos = {
                        'sessionName': login_response.json()['result']['sessionName'],
                        'userId': login_response.json()['result']['userId'],
                    }
                    self.session = datos
                    self.log.info(f"Se inicio seccion correctamente")
                else:
                    self.log.error(f"Error al iniciar sesión en Vtiger: {result.get('error', 'No se pudo iniciar sesión')}")
                    self.session = None
        except requests.RequestException as ex:
            self.log.error(f"Error al iniciar sesión en Vtiger: {ex}")
            self.session = None
        except KeyError as ex:
            self.log.error(f"Error al procesar la respuesta de Vtiger: {ex}")
            self.session = None
        except Exception as ex:
            self.log.error(f"Error inesperado al iniciar sesión en Vtiger: {ex}")
            self.session = None
    
    async def is_session_valid(self) -> bool:
        if not self.session or "sessionName" not in self.session:
            return False
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.url, params={
                    "operation": "listtypes",
                    "sessionName": self.session["sessionName"]
                },
                headers=self.headers
                )
                data = response.json()
                return data.get("success", False)
        except Exception as ex:
            self.log.error(f"Error al validar la sesión de Vtiger: {ex}")
            return False