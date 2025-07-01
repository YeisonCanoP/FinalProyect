
import sys 
sys.path.append('c:/Users/yeiso/OneDrive/Escritorio/Proyecto/final_proyect')
from app.core.secretManager import SecretManager
from app.utils.logger import Logger
#Clase para conectarme a la base de datos rds
class ConexionDB():

    def __init__(self):
        self.log = Logger("app/logs/ConexionDB.log").get_logger()
        self.host = "db-finaltech.c0hgqyu0au2e.us-east-1.rds.amazonaws.com"
        self.port = 3306
        self.user = "admin"
        self.password = SecretManager().get_secretRDS()

    def conectar(self):
        import mysql.connector
        try:
            connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
            )
            self.log.info("Intentando conectar a la base de datos...")
            if connection.is_connected():
                self.log.info("Conexion a la base de datos exitosa.")
            else:
                self.log.warning("No se pudo conectar a la base de datos.")
            return connection
        except mysql.connector.Error as err:
            self.log.info(f"Error: {err}")
            return None
    
    #Funcion para cerrar la conexion a la base de datos
    def close_connection(self, connection):
        if connection.is_connected():
            connection.close()
            self.log.info("Conexion cerrada exitosamente.")
        else:
            self.log.warning("Conexion ya estaba cerrada o no se pudo cerrar.")
    
    #Funcion para validar si hay conexion a la base de datos
    def is_connected(self, connection):
        if connection.is_connected():
            self.log.info("Conexion a la base de datos exitosa.")
            return True
        else:
            self.log.warning("No se pudo conectar a la base de datos.")
            self.conectar()
            return False
    
    #Funcion para ver las base de datos disponibles
    def show_databases(self, connection):
        if self.is_connected(connection):
            cursor = connection.cursor()
            cursor.execute("SHOW DATABASES")
            databases = cursor.fetchall()
            self.log.info("Bases de datos disponibles:")
            for db in databases:
                self.log.info(db[0])
            cursor.close()
        else:
            self.log.warning("No se pudo conectar a la base de datos para mostrar las bases de datos.")