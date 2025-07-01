import sys
sys.path.append('c:/Users/yeiso/OneDrive/Escritorio/Proyecto/final_proyect')
from app.core.conexionDB import ConexionDB
from app.utils.logger import Logger
import mysql.connector


#Clase para manejar todas las querys relacionado a cosnultas sobre la factura y detalles de factura, y para analisis
# de ventas
class Query_Facturas():

    def __init__(self):
        self.log = Logger("app/logs/Facturas.log").get_logger()
        self.con = ConexionDB().conectar()
    
    #Funcion para traer la facturas que se han generado en el dia
    async def traer_facturas_diaCantidad(self):
        try:
            if self.con is None:
                self.log.error("No se pudo conectar a la base de datos al hacer la consulta de facturas del dia")
                return None
            
            cur = self.con.cursor(dictionary=True)

            #Query para traer las facturas del dia la cantidad
            query = """
                SELECT SUM(total_facturas) as cantidad_facturas
                FROM ventas_diarias
                WHERE fecha = CURDATE();
            """
            cur.execute("USE analytics_db;") 
            cur.execute(query)
            result = cur.fetchone()

            return result["cantidad_facturas"] if result else 0

        except mysql.connector.Error as ex:
            self.log.info("Error al intentar mirar las facturas del dia: {ex}")
            self.log.error(f"Error al intentar traer las facturas del dia: {str(ex)}")
            return 0
        finally:
            if cur:
                cur.close()
            self.con.close()
    
    #Funcion para traer al cantidad de ventas del dia de hoy
    async def traer_ventas_diaValor(self):
        try:
            if self.con is None:
                self.log.error("No se pudo conectar a la base de datos al hacer la consulta de ventas del dia")
                return 0
            
            cur = self.con.cursor(dictionary=True)

            #Query para traer la cantidad de ventas del dia
            query = """
                SELECT COALESCE(SUM(total_ventas), 0) as total_ventasDia
                FROM ventas_diarias
                WHERE DATE(fecha) = CURDATE()
                AND YEAR(fecha) = YEAR(CURDATE());
            """
            cur.execute("USE analytics_db;") 
            cur.execute(query)
            result = cur.fetchone()

            return result["total_ventasDia"] if result else 0
        except mysql.connector.Error as ex:
            self.log.info(f"Error al intentar mirar las ventas del dia: {ex}")
            self.log.error(f"Error al intentar traer las ventas del dia: {str(ex)}")
            return 0
        finally:
            if cur:
                cur.close()
            self.con.close()
    
    #Fucnion para traer el valor de la suma de las ventas del mes, el total que se ha vendido en el mes
    async def traer_ventas_mesValor(self):
        try:
            if self.con is None:
                self.log.error("No se pudo conectar a la base de datos al hacer la consulta de ventas del mes")
                return 0
            
            cur = self.con.cursor(dictionary=True)
            #Query para traer el valor de la suma de las ventas del mes
            query = """
                SELECT COALESCE(SUM(total_ventas), 0) as total_ventasMes
                FROM ventas_diarias
                WHERE MONTH(fecha) = MONTH(CURDATE())
                AND YEAR(fecha) = YEAR(CURDATE());
            """
            cur.execute("USE analytics_db;") 
            cur.execute(query)
            result = cur.fetchone()
            return result["total_ventasMes"] if result else 0
        except mysql.connector.Error as ex:
            self.log.info("Error al intentar mirar las ventas del mes")
            self.log.error(f"Error al intentar traer las ventas del mes: {str(ex)}")
            return 0
        finally:
            if cur:
                cur.close()
            self.con.close()
    
    #Funcion para traer las ventas por dia de d hoy por horas para el analisis
    async def traer_ventas_horasAnalisis(self,horas):
        try:
            if self.con is None:
                self.log.error("No se pudo conectar a la base de datos al hacer la consulta de ventas por horas")
                return None
            
            cur = self.con.cursor()

            #Query para traer las ventas por horas
            query = """
            SELECT 
                DATE(fecha) AS fecha, 
                bloque_horario as hora, 
                SUM(total_ventas) AS total_ventas,
                SUM(total_facturas) AS total_facturas
            FROM venta_por_horas
            WHERE fecha >= DATE_SUB(NOW(), INTERVAL %s HOUR)
            GROUP BY fecha, hora
            ORDER BY fecha, hora;
            """
            cur.execute("USE analytics_db;") 
            cur.execute(query, (horas,))
            result = cur.fetchall()
            return result
        except mysql.connector.Error as ex:
            self.log.info(f"Error al intentar mirar las ventas de las ultimas {horas} horas: {ex}")
            self.log.error(f"Error al intentar traer las ventas de las ultimas {horas} horas: {str(ex)}")
            return None
        finally:
            if cur:
                cur.close()
            self.con.close()

    #Funcion para traer las ventas por dia, dependiendo de cuantos dias quiera ver el usuario
    async def traer_ventas_diaAnalisis(self, dias):
        try:
            if self.con is None:
                self.log.error("No se pudo conectar a la base de datos al hacer la consulta de ventas del dia")
                return None
            
            cur = self.con.cursor()

            #Query para traer las ventas del dia
            query = """
                SELECT DATE(fecha) AS fecha, SUM(total_ventas) AS total_ventas
                FROM ventas_diarias
                WHERE fecha >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
                GROUP BY DATE(fecha)
                ORDER BY fecha;
            """
            cur.execute("USE analytics_db;") 
            cur.execute(query,(dias,))
            result = cur.fetchall()
            return result
        except mysql.connector.Error as ex:
            self.log.info(f"Error al intentar mirar las ventas de los ultimos {dias} dias: {ex}")
            self.log.error(f"Error al intentar traer las ventas de los ultimos {dias} dias: {str(ex)}")
            return None
        finally:
            if cur:
                cur.close()
            self.con.close()

    #Funcion para traer las ventas por mes de todo el año
    async def traer_ventas_mesAnalisis(self):
        try:
            if self.con is None:
                self.log.error("No se pudo conectar a la base de datos al hacer la consulta de ventas del mes")
                return None
            
            cur = self.con.cursor()
            #Query para traer las ventas del mes
            query = """
                SELECT 
                    CONCAT(anio, '-', LPAD(mes, 2, '0')) AS fecha, 
                    total_ventas
                FROM ventas_mensuales
                WHERE anio = YEAR(CURDATE())  -- Filtra solo el año actual
                ORDER BY mes ASC;
            """
            cur.execute("USE analytics_db;") 
            cur.execute(query)
            result = cur.fetchall()
            return result
        except mysql.connector.Error as ex:
            self.log.info("Error al intentar mirar las ventas del año")
            self.log.error(f"Error al intentar traer las ventas del año: {str(ex)}")
            return None
        finally:
            if cur:
                cur.close()
            self.con.close()
    
    #Funcion para traer las ventas por año
    async def traer_ventas_anioAnalisis(self):
        try:
            if self.con is None:
                self.log.error("No se pudo conectar a la base de datos al hacer la consulta de ventas del año")
                return None
            
            cur = self.con.cursor()
            #Query para traer las ventas del año
            query = """
                SELECT 
                    anio AS fecha, 
                    total_ventas
                FROM ventas_anuales
                ORDER BY anio ASC;
            """
            cur.execute("USE analytics_db;") 
            cur.execute(query)
            result = cur.fetchall()
            return result
        except mysql.connector.Error as ex:
            self.log.info("Error al intentar mirar las ventas del año")
            self.log.error(f"Error al intentar traer las ventas del año: {str(ex)}")
            return None
        finally:
            if cur:
                cur.close()
            self.con.close()
    
    #Funcion para traer las categorias mas vendidas en lo que va del año para analisis
    async def traer_categoria_mesAnalisis(self):
        try:
            if self.con is None:
                self.log.error("No se pudo conectar a la base de datos al hacer la consulta de categorias del año")
                return None
            
            cur = self.con.cursor()
            #Query para traer las categorias mas vendidas del año
            query = """
                SELECT 
                    c.nombre AS categoria, 
                    COALESCE(SUM(cm.total_vendido),0) AS total_vendido, 
                    COALESCE(SUM(cm.cantidad),0) AS cantidad_vendida 
                FROM categorias_mas_vendidas cm
                JOIN categorias c ON cm.categoria_id = c.id
                WHERE cm.mes = MONTH(CURDATE())
                AND cm.anio = YEAR(CURDATE())
                GROUP BY c.nombre
                ORDER BY total_vendido DESC
                LIMIT 5;
            """
            cur.execute("USE analytics_db;") 
            cur.execute(query)
            result = cur.fetchall()
            return result
        except mysql.connector.Error as ex:
            self.log.info("Error al intentar mirar las categorias del año")
            self.log.error(f"Error al intentar traer las categorias del año: {str(ex)}")
            return None
        finally:
            if cur:
                cur.close()
            self.con.close()
    
    #Funcion para traer las categorias mas vendidas en lo que va del año
    async def traer_categorias_anioAnalisis(self):
        try:
            if self.con is None:
                self.log.error("No se pudo conectar a la base de datos al hacer la consulta de categorias del año")
                return None
            
            cur = self.con.cursor(dictionary=True)
            #Query para traer las categorias mas vendidas del año
            query = """
                SELECT 
                    c.nombre AS categoria, 
                    COALESCE(SUM(cm.total_vendido), 0) AS total_vendido, 
                    COALESCE(SUM(cm.cantidad), 0) AS cantidad_vendida
                FROM categorias_mas_vendidas cm
                JOIN categorias c ON cm.categoria_id = c.id
                WHERE cm.anio = YEAR(CURDATE())
                GROUP BY c.nombre
                ORDER BY total_vendido DESC
                LIMIT 5;
            """
            cur.execute("USE analytics_db;") 
            cur.execute(query)
            result = cur.fetchall()
            return result
        except mysql.connector.Error as ex:
            self.log.info("Error al intentar mirar las categorias del año")
            self.log.error(f"Error al intentar traer las categorias del año: {str(ex)}")
            return None
        finally:
            if cur:
                cur.close()
            self.con.close()
    
    #Fncion para traer los 5 prodcutos mas vendidos del mes
    async def traer_productos_mas_vendidosMes(self):
        try:
            if self.con is None:
                self.log.error("No se pudo conectar a la base de datos al hacer la consulta de productos del año")
                return None
            
            cur = self.con.cursor(dictionary=True)
            #Query para traer los 5 productos mas vendidos del año
            query = """
                SELECT 
                    p.nombre AS nombre,
                    pmv.total_vendido,
                    pmv.cantidad_vendida
                FROM productos_mas_vendidos pmv
                JOIN inventario p ON pmv.producto_id = p.id
                WHERE pmv.mes = MONTH(CURDATE())
                AND pmv.anio = YEAR(CURDATE())
                ORDER BY total_vendido DESC
                LIMIT 5;
            """
            cur.execute("USE analytics_db;") 
            cur.execute(query)
            result = cur.fetchall()
            return result
        except mysql.connector.Error as ex:
            self.log.info("Error al intentar mirar los productos del año")
            self.log.error(f"Error al intentar traer los productos del año: {str(ex)}")
            return None
        finally:
            if cur:
                cur.close()
            self.con.close()
    
    #Funcion para traer los 5 prodcutos mas vendidos del año
    async def traer_productos_mas_vendidosAnio(self):
        try:
            if self.con is None:
                self.log.error("No se pudo conectar a la base de datos al hacer la consulta de productos del año")
                return None
            
            cur = self.con.cursor(dictionary=True)
            #Query para traer los 5 productos mas vendidos del año
            query = """
                SELECT 
                    p.nombre AS nombre,
                    COALESCE(SUM(pmv.total_vendido),0) AS total_vendido,
                    COALESCE(SUM(pmv.cantidad_vendida),0) AS cantidad_vendida
                FROM productos_mas_vendidos_anuales pmv
                JOIN inventario p ON pmv.producto_id = p.id
                WHERE pmv.anio = YEAR(CURDATE())
                GROUP BY pmv.producto_id
                ORDER BY total_vendido DESC
                LIMIT 5;
            """
            cur.execute("USE analytics_db;") 
            cur.execute(query)
            result = cur.fetchall()

            return result
        except mysql.connector.Error as ex:
            self.log.info("Error al intentar mirar los productos del año")
            self.log.error(f"Error al intentar traer los productos del año: {str(ex)}")
            return None
        finally:
            if cur:
                cur.close()