
import asyncio
import sys
from datetime import datetime, timedelta
import pandas as pd
import httpx
import pytz 
sys.path.append("c:/Users/yeiso/OneDrive/Escritorio/Proyecto/final_proyect")
from app.core.conexionDB import ConexionDB
from app.utils.logger import Logger
from app.core.conexionVtgier import ConexionVtiger

#Clase para menjar todo lo del lambda que se va ejecutar cada 5 mn que va insertar informacion de vtiger a la base de datos
class Lambda:

    def __init__(self):
        self.con = ConexionDB().conectar()
        self.vtiger = ConexionVtiger()
        self.log = Logger("app/modules/lambda/logs/lambda.log").get_logger()

    def filtras_facturas(self, facturas):
        try:
            if self.con is None:
                self.log.error("No hay conexión a la base de datos.")
                return []

            if not facturas:
                return []

            # Obtener IDs de las facturas
            ids_facturas = [f["id"] for f in facturas]

            # Preparar consulta
            cur = self.con.cursor()
            cur.execute("USE analytics_db")
            formato_ids = ",".join(f"'{id_}'" for id_ in ids_facturas)

            query = f"""
                SELECT invoice_id FROM facturas_procesadas
                WHERE invoice_id IN ({formato_ids})
            """
            cur.execute(query)
            ids_existentes = {row[0] for row in cur.fetchall()}
            cur.close()

            # Filtrar solo las facturas nuevas
            nuevas = [f for f in facturas if f["id"] not in ids_existentes]

            self.log.info(
                f"Facturas nuevas detectadas: {len(nuevas)} de {len(facturas)} totales.")
            return nuevas

        except Exception as ex:
            self.log.error(f"Error al filtrar facturas nuevas: {ex}")
            return []
    
    #Funcion para guardar el resumen de ventas del día actual
    def guardar_resumen_dia(self, resumen):
        try:
            if self.con is None:
                self.log.error("No se pudo conectar a la base de datos.")
                return None
            
            cur = self.con.cursor()
            cur.execute("USE analytics_db")
            cur.execute("""
                INSERT INTO ventas_diarias (fecha, total_ventas, total_trasporte, total_facturas)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    total_ventas = VALUES(total_ventas),
                    total_trasporte = VALUES(total_trasporte),
                    total_facturas = VALUES(total_facturas);
            """, (
                resumen["fecha"],
                resumen["total_ventas"],
                resumen["total_transporte"],
                resumen["total_facturas"]
            ))

            self.con.commit()
            self.log.info(f"Resumen diario guardado: {resumen}")
            return True
        except Exception as ex:
            self.log.error(f"Error al guardar el resumen diario en la base de datos: {ex}")
            return False
        finally:
            cur.close()

    async def get_resumen_ventas_dia_actual(self):
        try:
            await self.vtiger.login()
            if not self.vtiger.session:
                self.log.error("No se pudo iniciar sesión en Vtiger.")
                return None

            zona_colombia = pytz.timezone("America/Bogota")
            ahora_col = datetime.now(zona_colombia).replace(minute=0, second=0, microsecond=0)
            hace_2_horas_col = ahora_col - timedelta(hours=2)

            # Convertir a UTC
            fecha_inicio = hace_2_horas_col.astimezone(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
            fecha_fin = ahora_col.astimezone(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")

            offset = 0
            limit = 100
            facturas = []

            self.log.info(f"Consultando facturas de {fecha_inicio} a {fecha_fin}...")

            while True:
                query = f"""
                    SELECT * FROM Invoice 
                    WHERE createdtime  >= '2025-06-26 00:00:00' AND createdtime  < '2025-06-27 00:00:00'
                    LIMIT {offset}, {limit};
                """
                params = {
                    "operation": "query",
                    "sessionName": self.vtiger.session["sessionName"],
                    "query": query.strip(),
                }

                async with httpx.AsyncClient() as client:
                    response = await client.get(self.vtiger.url, headers=self.vtiger.headers, params=params)
                    response.raise_for_status()
                    data = response.json()

                resultados = data.get("result", [])
                if not resultados:
                    break

                facturas.extend(resultados)
                if len(resultados) < limit:
                    break
                offset += limit

            if not facturas:
                self.log.info("No se encontraron facturas en este rango.")
                return None
            
            #Filtras las facturas ya registrada
            facturas_nuevas = self.filtras_facturas(facturas)
            if not facturas_nuevas:
                self.log.info("No hay facturas nuevas para procesar.")
                return None

            # Procesar resumen
            df = pd.DataFrame(facturas_nuevas)

            # Limpiar columnas necesarias
            df["total"] = df["hdnGrandTotal"].astype(float)
            df["transporte"] = df.get("hdnS_H_Amount", 0).astype(float) if "hdnS_H_Amount" in df.columns else 0.0  # Usa tu campo real aquí
            df["fecha"] = ahora_col.date()  # Usamos la fecha de hoy como clave

            resumen = {
                "fecha": df["fecha"].iloc[0],
                "total_ventas": df["total"].sum(),
                "total_transporte": df["transporte"].sum(),
                "total_facturas": len(df)
            }

            self.log.info(f"Resumen del día actual: {resumen}")
            if not self.guardar_resumen_dia(resumen):
                self.log.error("No se pudo guardar el resumen del día actual.")
                return None
            
            self.guardar_facturas_procesadas(facturas_nuevas, ahora_col.date())

        except Exception as ex:
            self.log.error(f"Error al obtener el resumen de ventas: {ex}")
            return None

    def guardar_facturas_procesadas(self, facturas, fecha):
        try:
            if self.con is None:
                self.log.error("No hay conexión a la base de datos.")
                return

            if not facturas:
                return

            cur = self.con.cursor()
            cur.execute("USE analytics_db")

            registros = [(f["id"], fecha) for f in facturas]
            cur.executemany("""
                INSERT IGNORE INTO facturas_procesadas (invoice_id, fecha)
                VALUES (%s, %s)
            """, registros)

            self.con.commit()
            cur.close()
            self.log.info(f"Registradas {len(registros)} facturas como procesadas.")
        except Exception as ex:
            self.log.error(f"Error al guardar facturas procesadas: {ex}")

    async def get_ventas_mensuales(self):
        try:
            zona_colombia = pytz.timezone("America/Bogota")
            hoy = datetime.now(zona_colombia)
            anio = hoy.year
            mes = hoy.month

            # Ejecutar consulta a la base de datos local
            with self.con.cursor() as cursor:
                # Asegurarse de que la base de datos está seleccionada
                cursor.execute("USE analytics_db")
                cursor.execute("""
                    SELECT 
                        SUM(total_ventas), 
                        SUM(total_trasporte), 
                        SUM(total_facturas)
                    FROM ventas_diarias
                    WHERE YEAR(fecha) = %s AND MONTH(fecha) = %s;
                """, (anio, mes))

                resultado = cursor.fetchone()
                total_ventas = resultado[0] or 0.0
                total_transporte = resultado[1] or 0.0
                total_facturas = resultado[2] or 0

                self.log.info(f"Ventas mensuales del {anio}-{mes}: ${total_ventas} en {total_facturas} facturas con transporte ${total_transporte}")

                # Insertar o actualizar en la tabla de resumen mensual
                cursor.execute("""
                    INSERT INTO ventas_mensuales (mes, anio, total_ventas, total_trasporte, total_facturas)
                    VALUES (%s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        total_ventas = VALUES(total_ventas),
                        total_trasporte = (total_trasporte),
                        total_facturas = VALUES(total_facturas);
                """, (mes, anio, total_ventas, total_transporte, total_facturas))

                self.con.commit()
                self.log.info(f"Resumen mensual insertado/actualizado correctamente: {anio}-{mes}")

        except Exception as ex:
            self.log.error(f"Error al obtener las ventas mensuales desde la base de datos: {ex}")
            return None

    #Fucnion para obtener las ventas anuales
    async def get_ventas_anuales(self):
        try:
            zona_colombia = pytz.timezone("America/Bogota")
            hoy = datetime.now(zona_colombia)
            anio = hoy.year

            with self.con.cursor() as cursor:
                cursor.execute("USE analytics_db")

                # Sumar las ventas del año actual desde ventas_mensuales
                cursor.execute("""
                    SELECT 
                        SUM(total_ventas),
                        SUM(total_trasporte),
                        SUM(total_facturas)
                    FROM ventas_mensuales
                    WHERE anio = %s;
                """, (anio,))

                resultado = cursor.fetchone()
                total_ventas = resultado[0] or 0.0
                total_transporte = resultado[1] or 0.0
                total_facturas = resultado[2] or 0

                self.log.info(f"Ventas anuales del {anio}: ${total_ventas} en {total_facturas} facturas con transporte ${total_transporte}")

                # Insertar o actualizar en la tabla de resumen anual
                cursor.execute("""
                    INSERT INTO ventas_anuales (anio, total_ventas, total_trasporte, total_facturas)
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        total_ventas = VALUES(total_ventas),
                        total_trasporte = VALUES(total_trasporte),
                        total_facturas = VALUES(total_facturas);
                """, (anio, total_ventas, total_transporte, total_facturas))

                self.con.commit()
                self.log.info(f"Resumen anual insertado/actualizado correctamente para {anio}")

        except Exception as ex:
            self.log.error(f"Error al obtener las ventas anuales desde la base de datos: {ex}")
            return None
        
    async def run(self):
        try:
            self.log.info("Iniciando proceso de resumen de ventas...")
            await self.get_resumen_ventas_dia_actual()
            await self.get_ventas_mensuales()
            await self.get_ventas_anuales()
            self.log.info("Proceso de resumen de ventas completado.")
        except Exception as ex:
            self.log.error(f"Error en el proceso de resumen de ventas: {ex}")


lambdaf = Lambda()
asyncio.run(lambdaf.get_resumen_ventas_dia_actual())
