
import sys
sys.path.append('c:/Users/yeiso/OneDrive/Escritorio/Proyecto/final_proyect')
from app.utils.logger import Logger
from app.core.conexionDB import ConexionDB

#Clase para insertar infomracion sobre los prducots mas vendiso es flasa, slo para funcionamineto
class ScriptsInsert:
    def __init__(self):
        self.con = ConexionDB()
        self.log = Logger("app/logs/scriptsInsert.log").get_logger()

    
    #Funcion
    def insert_productos(self):
        try:
            self.log.info("Iniciando insercion de productos")
            con = self.con.conectar()
            # Query para crear la tabla de inventario
            sql_create_inventory_table = """CREATE TABLE IF NOT EXISTS inventario(
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(60) NOT NULL UNIQUE,
                codigo VARCHAR(50) NOT NULL UNIQUE,
                marca VARCHAR(50) NOT NULL,
                cantidad INT DEFAULT 0,
                precio DECIMAL(15, 2) NOT NULL,
                descuento DECIMAL(5, 2) DEFAULT 0.00,
                deleted_at DATETIME DEFAULT NULL
            );
            """
            productos = [
                        (1, "Andamios", "A-001", "Vizora", 100, 50000, 0.05),
                        (2, "Encofrados (tacos cerchas y teleras)", "E-002", "Vizora", 120, 58333, 0.04),
                        (3, "Escaleras", "ESC-003", "Vizora", 80, 37500, 0.03),
                        (4, "Formaletas", "F-004", "Vizora", 90, 50000, 0.02),
                        (5, "Concretadoras", "C-005", "Vizora", 110, 54545, 0.01),
                    ]

            query = """
                INSERT INTO inventario (id, nombre, codigo, marca, cantidad, precio, descuento)
                VALUES (%s, %s, %s, %s, %s, %s, %s);
            """
            # Datos a insertar
            productos1 = [
                (1, 5000000, 100, 6, 2025),
                (2, 7000000, 120, 6, 2025),
                (3, 3000000, 80, 6, 2025),
                (4, 4500000, 90, 6, 2025),
                (5, 6000000, 110, 6, 2025),
            ]
            query1 = """
                INSERT INTO productos_mas_vendidos (producto_id, total_vendido, cantidad_vendida, mes, anio) 
                VALUES (%s, %s, %s, %s, %s);
            """
            cur = con.cursor()
            # Ejecutar la inserción
            cur.execute("USE analytics_db;")
            cur.execute(sql_create_inventory_table)
            cur.executemany(query, productos)
            cur.executemany(query1, productos1)
            con.commit()
            cur.close()
            con.close()
            self.log.info("Productos insertados correctamente")
        except Exception as e:
            self.log.error(f"Error al insertar productos: {e}")

    def insert_productos_anuales(self):
        try:
            self.log.info("Iniciando inserción de productos anuales")
            con = self.con.conectar()
            # Datos de ejemplo para el año 2025
            productos = [
                (1, 60000000, 1200, 2025),
                (2, 80000000, 1300, 2025),
                (3, 35000000, 950, 2025),
                (4, 55000000, 1000, 2025),
                (5, 75000000, 1100, 2025),
            ]
            query = """
                INSERT INTO productos_mas_vendidos_anuales (producto_id, total_vendido, cantidad_vendida, anio)
                VALUES (%s, %s, %s, %s);
            """
            cur = con.cursor()
            cur.execute("USE analytics_db;")
            cur.executemany(query, productos)
            con.commit()
            cur.close()
            con.close()
            self.log.info("Productos anuales insertados correctamente")
        except Exception as e:
            self.log.error(f"Error al insertar productos anuales: {e}")

ScriptsInsert().insert_productos()
ScriptsInsert().insert_productos_anuales()
