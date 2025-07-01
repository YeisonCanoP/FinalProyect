
from datetime import datetime
import asyncio
import sys

import pytz
sys.path.append('c:/Users/yeiso/OneDrive/Escritorio/Proyecto/final_proyect')
from app.core.conexionDB import ConexionDB
from app.utils.logger import Logger
from app.utils.utils import Utils
from app.utils.singleton import SingletonMeta

#Clase para manejar las consultas a la abse de datos para el analisis de datos de los container
class AnalisisContainer(metaclass=SingletonMeta):

    def __init__(self):
        self.con = ConexionDB().conectar()
        self.log = Logger("app/modules/analisis/logs/Analisis.log").get_logger()
        self.ingresosDiarios = 0
        self.ingresosMensuales = 0
        self.totalFacturas = 0
        self.transporteMes = 0

    #Funcion para ejecutrar toda la funcioes 
    async def run(self):
        try:
            await self.get_ventas_hoy()
            await self.get_ingresos_mes()
            await self.get_facturas_hoy()
            await self.get_transporte_mes()
        except Exception as ex:
            self.log.error(f"Error al ejecutar el analisis: {ex}")
    
    #FUncion para traer lo que se ha vendido en el dia de hoy
    async def get_ventas_hoy(self):
        try:
            if not self.con.is_connected():
                self.log.error("No hay conexion a la base de datos.")
                return None
            self.log.info("Obteniendo ventas del dia de hoy...")
            zona_colombia = pytz.timezone("America/Bogota")
            fecha = datetime.now(zona_colombia).strftime("%Y-%m-%d")
            cursor = self.con.cursor()
            cursor.execute("USE analytics_db;")  # Asegurarse de usar la base de datos correcta
            query = """
                SELECT total_ventas FROM ventas_diarias WHERE fecha = %s;
            """
            cursor.execute(query,(fecha,))
            result = cursor.fetchone()
            if result:
                total_ventas = Utils().formatNumero(result[0])
                self.ingresosDiarios = total_ventas
            else:
                self.log.info("No se encontraron ventas para el dia de hoy.")
                return 0
        except Exception as e:
            self.log.error(f"Error al obtener las ventas del dia: {e}")
            return None
        finally:
            cursor.close()
        
    #Funcion para trear la cantidad de facutras generadas en el dia de hoy
    async def get_facturas_hoy(self):
        try:
            if not self.con.is_connected():
                self.log.error("No hay conexion a la base de datos.")
                return None
            zona_colombia = pytz.timezone("America/Bogota")
            fecha = datetime.now(zona_colombia).strftime("%Y-%m-%d")
            cursor = self.con.cursor()
            cursor.execute("USE analytics_db;")  # Asegurarse de usar la base de datos correcta
            query = """
                SELECT total_facturas FROM ventas_diarias WHERE fecha = %s;
            """
            cursor.execute(query, (fecha,))
            result = cursor.fetchone()
            if result:
                total_facturas = result[0]
                self.totalFacturas =  total_facturas
            else:
                self.log.info("No se encontraron facturas para el dia de hoy.")
                return 0
        except Exception as e:
            self.log.error(f"Error al obtener las facturas del dia: {e}")
            return None
        finally:
            cursor.close()

    #Funcion para traer los ingresos del mes
    async def get_ingresos_mes(self):
        try:
            if not self.con.is_connected():
                self.log.error("No hay conexion a la base de datos.")
                return None
            
            cursor = self.con.cursor()
            cursor.execute("USE analytics_db;")  # Asegurarse de usar la base de datos correcta
            query = """
                SELECT SUM(total_ventas) FROM ventas_diarias WHERE MONTH(fecha) = MONTH(CURDATE()) AND YEAR(fecha) = YEAR(CURDATE());
            """
            cursor.execute(query)
            result = cursor.fetchone()
            if result and result[0] is not None:
                total_ingresos = Utils().formatNumero(result[0])
                self.ingresosMensuales =  total_ingresos
            else:
                self.log.info("No se encontraron ingresos para el mes actual.")
                return 0
        except Exception as e:
            self.log.error(f"Error al obtener los ingresos del mes: {e}")
            return None
        finally:
            cursor.close()
    
    #Funcion para trear cuanto se ha generado de trasporte este mes
    async def get_transporte_mes(self):
        try:
            if not self.con.is_connected():
                self.log.error("No hay conexion a la base de datos.")
                return None
            
            cursor = self.con.cursor()
            cursor.execute("USE analytics_db;")  # Asegurarse de usar la base de datos correcta
            query = """
                SELECT SUM(total_trasporte) FROM ventas_diarias WHERE MONTH(fecha) = MONTH(CURDATE()) AND YEAR(fecha) = YEAR(CURDATE());
            """
            cursor.execute(query)
            result = cursor.fetchone()
            if result and result[0] is not None:
                total_transporte = Utils().formatNumero(result[0])
                self.transporteMes =  total_transporte
            else:
                self.log.info("No se encontraron ingresos por transporte para el mes actual.")
                return 0
        except Exception as e:
            self.log.error(f"Error al obtener los ingresos por transporte del mes: {e}")
            return None
        finally:
            cursor.close()