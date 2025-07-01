import sys
import pandas as pd
import unicodedata
sys.path.append('c:/Users/yeiso/OneDrive/Escritorio/Proyecto/final_proyect')
from app.core.conexionDB import ConexionDB
from app.utils.logger import Logger
from mysql.connector import Error

#Clase para organziar uncvs de vtiger a la base de datos
class OrganizadorCVS:

    def __init__(self):
        self.con = ConexionDB().conectar()
        self.log = Logger("app/models/organziadorcvs.log").get_logger()
    

    #Funcion para organziar el cvs de vtiger
    def organziar_cvs(self):
        try:
            if self.con is None:
                self.log.error("No se pudo conectar a la base de datos.")
                return None
            
            #Se abre en pandas
            df = pd.read_csv("app/data/Informe_detallado_de_Facturas_20250625_145553.csv")

            #Organizo los espacio del dataframe
            df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
            #Eliminar las tildes de las columnas que no son necesarias
            df.columns = [
            ''.join(
                c for c in unicodedata.normalize('NFKD', col)
                if not unicodedata.combining(c)
            )
            for col in df.columns
        ]

            #Quito los simbolos de pesos, comas  y lo convierto a float
            df['total'] = df['total'].replace({r'\$':''}, regex=True).str.replace(',', '').astype(float)

            #Fecha de creacion a datetime
            fila_cargo =  df[df.iloc[:, 0].astype(str).str.contains("Facturas cargos", case=False, na=False)]
            # Si existe esa fila, extraemos el valor
            transporte_total = 0
            if not fila_cargo.empty:
                try:
                    transporte_total = fila_cargo.iloc[0, 1]  # Segunda columna, donde está el valor
                    # Convertimos a número si es string con $
                    if isinstance(transporte_total, str):
                        transporte_total = transporte_total.replace("$", "").replace(",", "")
                        transporte_total = float(transporte_total)
                except Exception as e:
                    self.log.warning(f"No se pudo extraer transporte_total: {e}")
                    # Eliminamos esa fila del DataFrame para no dañar el análisis
                    df = df[~df.iloc[:, 0].astype(str).str.contains("Facturas cargos", case=False, na=False)]

            # Guardamos como nueva columna en todo el DataFrame (opcional si quieres replicarlo)
            df["transporte_total"] = transporte_total

            df['fecha_de_creacion'] = pd.to_datetime(df['fecha_de_creacion'], format="%d-%m-%Y %H:%M:%S", errors='coerce')

            # Eliminar filas con errores
            df = df.dropna(subset=['fecha_de_creacion'])
    
            #extrear el mes y el anio
            df['mes'] = df['fecha_de_creacion'].dt.month.fillna(0).astype(int)
            df['anio'] = df['fecha_de_creacion'].dt.year.fillna(0).astype(int)
            df['fecha'] = df['fecha_de_creacion'].dt.date

            #Y agrupar por mes y año
            resumen_mes = df.groupby(['mes', 'anio']).agg(
                total_ventas=pd.NamedAgg(column='total', aggfunc='sum'),
                total_transporte=pd.NamedAgg(column='transporte_total', aggfunc='first'),
                total_facturas=pd.NamedAgg(column='numero_factura', aggfunc='count')
            ).reset_index()
            #Agrupar por año, mes y día
            resumen_dia = df.groupby(['fecha']).agg(
                total_ventas=pd.NamedAgg(column='total', aggfunc='sum'),
                total_facturas=pd.NamedAgg(column='numero_factura', aggfunc='count')
            ).reset_index()

            #Log para ver si el resumen se creo correctamente
            self.log.info("Resumen de ventas por mes y año creado correctamente.")
            self.log.info(resumen_mes.to_string(index=False))

            return resumen_mes, resumen_dia

        except Error as ex:
            self.log.error(f"Error al organziar el cvs: {ex}")
        finally:
            self.con.close()
    
    # Funcion para guardar el resumen en la base de datos
    def guardar_resumen(self, resumen_mes, resumen_dia):
        cur = None
        try:
            if self.con is None:
                self.log.error("No se pudo conectar a la base de datos.")
                return None
            
            cur = self.con.cursor()

            # Insertar el resumen mensual
            for _, row in resumen_mes.iterrows():
                cur.execute("USE analytics_db;")
                cur.execute("""
                    INSERT INTO ventas_mensuales (mes, anio, total_ventas, total_trasporte, total_facturas)
                    VALUES (%s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        total_ventas = VALUES(total_ventas),
                        total_trasporte = VALUES(total_trasporte),
                        total_facturas = VALUES(total_facturas);
                """, (
                    int(row['mes']),
                    int(row['anio']),
                    float(row['total_ventas']),
                    float(row['total_transporte']),
                    int(row['total_facturas'])
                ))
            
            # Insertar el resumen diario
            for _, row in resumen_dia.iterrows():
                cur.execute("USE analytics_db;")
                cur.execute("""
                    INSERT INTO ventas_diarias (fecha, total_ventas, total_facturas)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        total_ventas = VALUES(total_ventas),
                        total_facturas = VALUES(total_facturas);
                """, (
                    row['fecha'],
                    float(row['total_ventas']),
                    int(row['total_facturas'])
                ))
            
            self.con.commit()
            self.log.info("Resumen guardado en la base de datos correctamente.")

        except Error as ex:
            self.log.error(f"Error al guardar el resumen en la base de datos: {ex}")
        finally:
            if cur:
                cur.close()
            self.con.close()