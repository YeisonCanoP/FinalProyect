import asyncio
from datetime import datetime
import sys
import httpx
sys.path.append("c:/Users/yeiso/OneDrive/Escritorio/Proyecto/final_proyect")
from app.core.conexionVtgier import ConexionVtiger
from app.utils.logger import Logger
from app.utils.singleton import SingletonMeta


# Clase para traer todo los datos y todo lo relacionado a vtiger
class Vtiger(metaclass=SingletonMeta):

    def __init__(self):
        self.vtiger = ConexionVtiger()
        self.log = Logger("app/modules/vtgier/logs/Vtiger.log").get_logger()
        self.headers = {"User-Agent": "Mozilla/5.0"}
        self.url = self.vtiger.url
        self.cantidadProductos = 0
        self.newClients = 0
        self.cotizaciones = 0
    
    async def _init(self):
        try:
            while True:
                await asyncio.sleep(2)
                await self.get_new_clients()
                await self.get_product_count()
                await self.get_quote_count()
                await asyncio.sleep(300)
        except Exception as ex:
            self.log.error(f"Error al inicializar Vtiger: {ex}")

    # Funcion para traer los clientes nuevo que fueron registrado en el dia de hoy
    async def get_new_clients(self):
        try:
            await self.vtiger.login()
            if not self.vtiger.session:
                self.log.error("No se pudo iniciar sesión en Vtiger.")
                return None
            fecha_hoy = datetime.now().strftime("%Y-%m-%d")
            query = f"SELECT COUNT(*) FROM Accounts WHERE createdtime >= '{fecha_hoy} 00:00:00';"

            # parametros
            params = {
                "operation": "query",
                "sessionName": self.vtiger.session["sessionName"],
                # Esto es cuenta
                "query": query,
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.url, headers=self.headers, params=params
                )
                response.raise_for_status()
                data = response.json()
            if "result" in data:
                self.newClients = int(data["result"][0]["count"])
            else:
                self.log.error(
                    "No se encontraron resultados en la respuesta de Vtiger."
                )
                return None

        except Exception as e:
            self.log.error(f"Error al obtener los clientes nuevos: {e}")
            return None

    # Funcion para traer la cantidad de prodducto que hay en la base de datos
    async def get_product_count(self):
        try:
            await self.vtiger.login()
            if not self.vtiger.session:
                self.log.error("No se pudo iniciar sesión en Vtiger.")
                return None

            query = "SELECT COUNT(*) FROM Products;"

            params = {
                "operation": "query",
                "sessionName": self.vtiger.session["sessionName"],
                "query": query,
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.url, headers=self.headers, params=params
                )
                response.raise_for_status()
                data = response.json()

            if "result" in data:
                self.cantidadProductos= int(data["result"][0]["count"])
            else:
                self.log.error(
                    "No se encontraron resultados en la respuesta de Vtiger."
                )
                return None
        except Exception as e:
            self.log.error(f"Error al obtener el conteo de productos: {e}")

    # Funcion para traer la cantidad de contizacion que se han realizado en este dia
    async def get_quote_count(self):
        try:
            await self.vtiger.login()
            if not self.vtiger.session:
                self.log.error("No se pudo iniciar sesión en Vtiger.")
                return None

            fecha_hoy = datetime.now().strftime("%Y-%m-%d")
            query = f"SELECT COUNT(*) FROM Quotes WHERE createdtime >= '{fecha_hoy} 00:00:00';"

            params = {
                "operation": "query",
                "sessionName": self.vtiger.session["sessionName"],
                "query": query,
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.url, headers=self.headers, params=params
                )
                response.raise_for_status()
                data = response.json()

            if "result" in data:
                self.cotizaciones = int(data["result"][0]["count"])
            else:
                self.log.error(
                    "No se encontraron resultados en la respuesta de Vtiger."
                )
                return None
        except Exception as e:
            self.log.error(f"Error al obtener el conteo de cotizaciones: {e}")
            return None
    
    # Funcion para descrbiri algo
    async def describe(self):
        try:
            await self.vtiger.login()
            if not self.vtiger.session:
                self.log.error("No se pudo iniciar sesión en Vtiger.")
                return None

            params = {
                "operation": "describe",
                "sessionName": self.vtiger.session["sessionName"],
                "elementType": "Accounts",
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.url, headers=self.headers, params=params
                )
                response.raise_for_status()
                data = response.json()

                self.log.info(f"Respuesta de Vtiger: {data}")
            return data["result"]
        except Exception as e:
            self.log.error(f"Error al describir Accounts: {e}")
            return None
