import sys
sys.path.append('c:/Users/yeiso/OneDrive/Escritorio/Proyecto/final_proyect')
from app.core.conexionDB import ConexionDB
from mysql.connector import Error
from app.utils.logger import Logger


#Clase para manejar la creacion de las tablas de la base de datos
class CreateDB:

    def __init__(self):
        self.log = Logger("app/logs/CreateDB.log").get_logger()
        self.db = ConexionDB()
        self.con = self.db.conectar()
        self.cur = self.con.cursor()

    #Primero creo la base de datos
    def create_database(self):
        try:
            self.cur.execute("CREATE DATABASE IF NOT EXISTS analytics_db")
            self.db.log.info("Base de datos creada exitosamente.")
            self.create_table_productos()
        except Error as ex:
            self.db.log.error(f"Error al crear la base de datos: {ex}")
            raise ex
        finally:
            self.cur.close()
            self.con.close()
    
    #Funcion para crear la tabla de productos
    def create_table_productos(self):
        try:
            if self.con is None:
                self.log.info("No se pudo conectar a la base de datos en la creacion de la tabla productos")
                return None

            query = """
            CREATE TABLE IF NOT EXISTS inventario (
                id INT AUTO_INCREMENT PRIMARY KEY,
                cantidad_productos INT NOT NULL
            );
            """
            # Se abre el cursor y se ejecuta el comando
            cur = self.con.cursor()
            cur.execute("USE analytics_db")  # Cambiar a la base de datos creada
            cur.execute(query)

            # Se hace el commit y se cierra el cursor
            self.con.commit()
            self.log.info("Tabla de productos creada exitosamente.")
            self.create_tablas_materialziada()
        except Error as ex:
            self.log.error(f"Error al crear la tabla de productos: {ex}")
        finally:
            cur.close()

    #Funcion para crear las tablas materialziada para ifnormacion de las graficas
    def create_tablas_materialziada(self):
        try:
            if self.con is None:
                self.log.info("No se pudo conectar a la base de datos en la creacion de las tablas materializadas")
                return None

            query_diarias="""CREATE TABLE ventas_diarias (
                fecha DATE NOT NULL PRIMARY KEY,
                total_ventas DECIMAL(15,2) NOT NULL,
                total_trasporte DECIMAL(15,2) NOT NULL,
                total_facturas INT NOT NULL
            );
            """

            query_mensuales="""CREATE TABLE ventas_mensuales (
                anio INT NOT NULL,
                mes INT NOT NULL,
                total_ventas DECIMAL(15,2) NOT NULL,
                total_trasporte DECIMAL(15,2) NOT NULL,
                total_facturas INT NOT NULL,
                PRIMARY KEY (anio, mes)
            );
            """

            query_anuales="""CREATE TABLE ventas_anuales (
                anio INT NOT NULL PRIMARY KEY,
                total_ventas DECIMAL(15,2) NOT NULL,
                total_trasporte DECIMAL(15,2) NOT NULL,
                total_facturas INT NOT NULL
            );
            """

            #Funcion para crear la tabla de producto mas vendidos del mes
            query_producto_mas_vendidos="""
                CREATE TABLE productos_mas_vendidos (
                    producto_id INT NOT NULL,
                    total_vendido DECIMAL(15,2) NOT NULL,
                    cantidad_vendida INT NOT NULL,
                    mes INT NOT NULL,
                    anio INT NOT NULL,
                    PRIMARY KEY (producto_id, mes, anio),
                    FOREIGN KEY (producto_id) REFERENCES inventario(id) ON DELETE CASCADE
                );
            """

            #Funcion para crear la tabla de productos mas vendidos anuales
            query_producto_mas_vendidos_anuales="""
                CREATE TABLE productos_mas_vendidos_anuales (
                    producto_id INT NOT NULL,
                    total_vendido DECIMAL(15,2) NOT NULL,
                    cantidad_vendida INT NOT NULL,
                    anio INT NOT NULL,
                    PRIMARY KEY (producto_id, anio),
                    FOREIGN KEY (producto_id) REFERENCES inventario(id) ON DELETE CASCADE
                );
            """

            #Indexz para las tabals
            query_index=[
                "CREATE INDEX idx_productos_anio ON productos_mas_vendidos_anuales (anio);",
                "CREATE INDEX idx_fecha_diaria ON ventas_diarias (fecha);",
                "CREATE INDEX idx_anio_mensuales ON ventas_mensuales (anio);",
                "CREATE INDEX idx_mes_mensuales ON ventas_mensuales (mes);",
                "CREATE INDEX idx_anio_anuales ON ventas_anuales (anio);",
            ]
            # Se abre el cursor y se ejecuta el comando
            cur = self.con.cursor()
            cur.execute("USE analytics_db")  # Cambiar a la base de datos creada
            cur.execute(query_diarias)
            cur.execute(query_mensuales)
            cur.execute(query_anuales)
            cur.execute(query_producto_mas_vendidos)
            cur.execute(query_producto_mas_vendidos_anuales)

            for index in query_index:
                cur.execute(index)

            # Se hace el commit y se cierra el cursor
            self.con.commit()
            self.log.info("Se creo las tabals materializadas")
        except Error as ex:
            self.log.error(f"Error al crear las tablas materializadas: {ex}")
            self.log.info(f"Error al crear las tablas materializadas: {ex}")
        finally:
            cur.close()
    
    #Crear 2 usuarios bases para la tabla de usuarios
    def create_base_users(self):
        try:
            if self.con is None:
                self.log.info("No se pudo conectar a la base de datos en la creacion de los usuarios bases")
                return None
        
            query = """
            INSERT INTO usuarios (nombre, email, contrasena, login_tipo)
            VALUES
            ('Admin', 'cano@gmail.com', 'admin123', 'basic'),
            ('User', 'pedrito@gmail.com', 'user123', 'basic')
            ON DUPLICATE KEY UPDATE
                nombre = VALUES(nombre),
                contrasena = VALUES(contrasena),
                login_tipo = VALUES(login_tipo);
            """
            # Se abre el cursor y se ejecuta el comando
            cur = self.con.cursor()
            cur.execute("USE analytics_db")  # Cambiar a la base de datos creada
            cur.execute(query)
            # Se hace el commit y se cierra el cursor
            self.con.commit()
            self.log.info("Usuarios bases creados exitosamente.")
        except Error as ex:
            self.log.error(f"Error al crear los usuarios bases: {ex}")
        finally:
            cur.close()
            self.con.close()