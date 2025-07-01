import asyncio
import os
import tempfile
import webbrowser
import flet as ft
from flet.plotly_chart import PlotlyChart
import numpy as np
import plotly.express as px
import pandas as pd
import sys
sys.path.append('c:/Users/yeiso/OneDrive/Escritorio/Proyecto/final_proyect')
from utils.logger import Logger
from app.modules.analisis.querys.facturas import Query_Facturas
from utils.singleton import SingletonMeta
from app.core.conexionDB import ConexionDB
from utils.utils import Utils
from app.modules.analisis.graficaPastel import GraficaPastel


#Clase para manejar todo lo relacionado a la graficas que se necesita en tablero, como la de ventas y la de prodcutos mas vendidps
class GraficaLineal(metaclass=SingletonMeta):
    def __init__(self,view):
        self.view = view
        self.page = view.page
        self.graficaPastel = GraficaPastel(view)
        self.log = Logger("app/logs/Graficas.log").get_logger()
        self.grafica = None
        self.colorLetra = "#0D0630"
        self.con = ConexionDB()

    #Funcion para verificar si se debe generar la factura, si hay conexion a la base de datos o no
    def validar_generacion(self):
        #Si no hay conexion a la base de datos se retorna False
        if self.con.conectar() is not None:
            self.con.close_connection()
            #Si hay conexion a la base de datos se retorna True
            return True
        else:
            self.con.close_connection()
            self.log.error("No hay conexion a la base de datos, no se puede generar la factura")
            return False

    #Funcion para calcular el tick format
    def tick_format(self, x):
        #Donde x es el valor
        if x >= 1_000_000_000:
            return f"{x/1_000_000_000:.1f} Mil M"
        elif x >= 1_000_000:
            return f"{x/1_000_000:.1f} M"
        elif x >= 1_000:
            return f"{x/1_000:.1f} Mil"
        return str(int(x))

    #Funcion para crear la grafica dependiendo del tipo
    async def obtener_panda(self,tipo,dias=None):
        try:
            df = None
            #Se busca el tipo de analisis que se paso
            match tipo:
                #Si es dias, por defecto se traen los ultimos 7 dias, pero el usuairo puede elegir, en un dropdown
                #entre 7,30, y 90 dias
                case "dias":
                    #Traigo los datos con la query para el analisis por dias
                    datos = await Query_Facturas().traer_ventas_diaAnalisis(dias)

                    #Si los datos son None se return
                    if not datos:
                        self.log.error("No se pudieron obtener los datos para la grafica de ventas por dias")
                        return None
                    

                    #Paso los datos a pandas para poder usar plotly
                    df = pd.DataFrame(datos, columns=["Fecha", "Ventas"])

                    #Se conviete ventas en float
                    df["Ventas"] = df["Ventas"].astype(float)

                    #Se comvierte la fecha en datatime
                    df["Fecha"] = pd.to_datetime(df["Fecha"]).dt.strftime("%d/%m")  # Dia/Mes


                #Si es por mes, se muestran todos los meses del año actual en el que este
                case "mes":
                    #Traigo los datos con la query para el analisis por mes
                    datos = await Query_Facturas().traer_ventas_mesAnalisis()

                    #Si los datos son None se return
                    if not datos:
                        self.log.error("No se pudieron obtener los datos para la grafica de ventas por mes")
                        return None

                    #Paso los datos a pandas para poder usar plotly
                    df = pd.DataFrame(datos, columns=["Fecha", "Ventas"])

                    #Se conviete ventas en float
                    df["Ventas"] = df["Ventas"].astype(float)

                    #Se convierte la fecha en datatime
                    df["Fecha"] = pd.to_datetime(df["Fecha"] + "-01").dt.strftime("%m/%Y")  # Mes/Año

                case "anio":

                    #Traigo los datos con la query para el analisis por año
                    datos = await Query_Facturas().traer_ventas_anioAnalisis()

                    #Si los datos son None se return
                    if not datos:
                        self.log.error("No se pudieron obtener los datos para la grafica de ventas por año")
                        return None

                    #Paso los datos a pandas para poder usar plotly
                    df = pd.DataFrame(datos, columns=["Fecha", "Ventas"])

                    #Se conviete ventas en float
                    df["Ventas"] = df["Ventas"].astype(float)
                    #Se convierte la fecha en datatime
                    df["Fecha"] = df["Fecha"].astype(str)  # Solo Año

            # 🔹 Verificación final antes de retornar `df`
            if df is None or df.empty:
                self.log.error(f"Tipo de análisis desconocido: {tipo}")
                return None
            return df

        except Exception as ex:
            self.log.info(f"Error al intentar obtene rlos datos pandas:{ex}")
            self.log.error(f"Error al intentar obtener los datos pandas: {ex}")
            return None
        
    #Funcion para crear la grafica con los datos pandas
    async def crear_grafica(self, df,tipo,dias,web=False):
        try:
            #Si el dataframe es None se return
            if df is None or df.empty:
                self.log.error("No se pudo crear la grafica, el dataframe es None")
                return None
            
            #Se crea la grafica con plotly
            fig = px.line(df, x="Bloque_Horario" if tipo =="horas" else "Fecha", y="Ventas", markers=True)
            #Se ajusta los traces
            fig.update_traces(
                marker=dict(size=8),
                hoverinfo="text+name",
                hovertemplate="Fecha: %{x}<br>Ventas: " + df["Ventas"].apply(lambda x: Utils().formatNumero(x)).astype(str),
                text=df["Ventas"]
            )

            #Se ajusta el tamaño de la grafica
            if web:
                fig.update_layout(
                    font=dict(
                        family="Poppins",
                        size=14,  # Tamaño de fuente más grande si es web
                        color=self.colorLetra
                    ),
                    xaxis_title="Horas" if tipo == "horas" else "Fecha",
                    margin=dict(t=20, b=20, l=50, r=20),  # Márgenes más ajustados para web
                    width=(
                        1200 if dias == 7
                        else 1450 if dias == 30
                        else 1600 if dias == 90
                        else 1200 if tipo == "mes"
                        else 1200 if tipo == "anio"
                        else 1300
                    ),  # Un ancho más grande para web
                    height=550  # Altura específica para web
                )
            else:
                fig.update_layout(
                    font=dict(
                        family="Poppins",
                        size=12,
                        color=self.colorLetra
                    ),
                    xaxis_title="Horas" if tipo == "horas" else "Fecha",
                    margin=dict(t=2, b=30, l=60, r=2),
                    width=(
                        1200 if dias == 7
                        else 1400 if dias == 30
                        else 1600 if dias == 90
                        else 1200 if tipo == "mes"
                        else 1300 if tipo == "anio"
                        else 1100
                    ),
                    height=350
                )
                #Se configura la apariencia de la grafica
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)", 
                    #Color d ela cuadricula
                    xaxis=dict(
                        gridcolor="rgb(224, 224, 224)", 
                        showgrid=True  
                    ),
                    yaxis=dict(
                        gridcolor="rgb(224, 224, 224)", 
                        showgrid=True      
                    ),
                )

            #Obtiene el valor mínimo y máximo de Ventas
            min_val = df["Ventas"].min()
            max_val = df["Ventas"].max()

            #Define una cantidad razonable de ticks
            num_ticks = 6  # Puedes ajustarlo según la necesidad

            #Genera los valores de los ticks de manera uniforme
            tick_vals = list(np.linspace(min_val, max_val, num_ticks))

            #Formatea los valores de los ticks
            tick_texts = [self.tick_format(tick) for tick in tick_vals]

            #Aplica los ticks a la gráfica
            fig.update_yaxes(tickvals=tick_vals, ticktext=tick_texts)

            padding = (max(df["Ventas"]) - min(df["Ventas"])) * 0.1  # Un 10% de margen
            fig.update_yaxes(
                range=[min(df["Ventas"]) - padding, max(df["Ventas"]) + padding],
            )

            if tipo == "horas":
                fig.update_xaxes(
                    type="category",
                    )           
            return fig
        except Exception as ex:
            self.log.info(f"Error al intentar crear la grafica:{ex}")
            self.log.error(f"Error al intentar crear la grafica: {ex}")
            return None

    #Funcion para mostrar la grafica en flet
    async def mostrar_grafica(self,tipo="dias",dias=7):
        try:
            #Datospara la grafica
            df = await self.obtener_panda(tipo,dias)
            
            #Si no se pudo obtener los datos pandas se return
            if df is None or df.empty:
                self.log.error("No se pudo mostrar la grafica, el dataframe es None en la funcion Mostrar Grafica")
                await self.mostrar_grafica_vacia()
                return

            #Se crea la grafica con plotly con los datos de pandas
            fig = await self.crear_grafica(df,tipo,dias)

            #Si no se pudo crear la grafica se return
            if not fig:
                self.log.error("No se pudo mostrar la grafica, la figura es None en la funcion Mostrar Grafica")
                await self.mostrar_grafica_vacia()
                return
            
            #Se crea la grafica dentro de un responsiveRow
            grafica = ft.Row(
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.START,
                expand=True,
                scroll=ft.ScrollMode.ALWAYS,
                controls = [
                    PlotlyChart(figure=fig,expand=True,original_size=True,data=(tipo,dias)),
                ]
            )

            self.grafica = grafica

        except Exception as ex:
            self.log.info(f"Error al intentar mostrar la grafica:{ex}")
            self.log.error(f"Error al intentar mostrar la grafica: {ex}")
            return None
    
    #Funcion para actualizar la grafica a el tipo que eliga el usuario
    async def actualizar_grafica(self,tipo):
        #from utils.graficaPastel import GraficaPastel

        try:
            graficaTablero = self.view.refColumnaGraficaProductividad.current
            match tipo:
                #Si el tipo es 24 horas, se le asigna el valor de None a dias y se le asigna el tipo de horas
                case "horas":
                    dias = None
                    tipo="horas"
                
                #Si el tipo es 7,30 o 90 se le asigna el valor de dias a la variable dias y se le asigna el tipo de dias
                case "7":
                    dias = 7
                    tipo="dias"
                
                case "30":
                    dias = 30
                    tipo="dias"
                
                case "90":
                    dias = 90
                    tipo="dias"
                
                case "mes":
                    tipo="mes"
                    dias = None

                    await GraficaPastel().actualizar_grafica(tipo)
                
                case "anio":
                    tipo="anio"
                    dias = None

                    await GraficaPastel().actualizar_grafica(tipo)

                case _:
                    self.log.info(f"Tipo de analisis desconocido: {tipo}")
                    self.log.error(f"Tipo de análisis desconocido: {tipo}")
                    return None

            await self.mostrar_grafica(tipo,dias)

            graficaTablero.content = self.grafica
            graficaTablero.update()

        except Exception as ex:
            self.log.info(f"Error al intentar actualizar la grafica:{ex}")
            self.log.error(f"Error al intentar actualizar la grafica: {ex}")
            return None

    #Fucnion para mostrar lo que aparecera cada vez que no hayan datos o no se pueda mostrar la grafica
    async def mostrar_grafica_vacia(self):
        try:
            # Estoe s temoral esta sera la grafica de error
            grafica = ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
                expand=True,
                controls=[
                    # Titulo de error 
                    ft.Container(
                        alignment=ft.alignment.center,
                        content=ft.Text(
                            "No hay datos disponibles para la gráfica de productividad.",
                            style=ft.TextStyle(
                                size=16,
                                color=self.colorLetra,
                                weight=ft.FontWeight.W_500,
                                font_family="Poppins",
                            ),
                        ),
                    ),
                    # Icono de carita triste
                    ft.Icon(
                        ft.Icons.SENTIMENT_DISSATISFIED,
                        size=50,
                        color=self.colorLetra,
                    ),
                ],
            )

            self.grafica = grafica

        except Exception as ex:
            self.log.info(f"Error al intentar mostrar la grafica:{ex}")
            self.log.error(f"Error al intentar mostrar la grafica: {ex}")
            return None

    #Funcion para actualizar la grafica
    async def mostrar_graficaEnWeb(self,web,e):
        try:
            tipo,dias = self.grafica.controls[0].data
            df = await self.obtener_panda(tipo, dias)
            if df is None or df.empty:
                self.log.error("No se pudo mostrar la grafica, el dataframe es None en la funcion Mostrar Grafica")
                return 
            fig = await self.crear_grafica(df, tipo,dias,web)
            if not fig:
                self.log.error("No se pudo mostrar la grafica, la figura es None en la funcion Mostrar Grafica")
                return 

            # Guardar HTML temporal (como lo hace internamente fig.show())
            with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode="w", encoding="utf-8") as f:
                f.write(fig.to_html(include_plotlyjs="cdn"))
                filepath = f.name

            # Abrir archivo HTML directamente en el navegador del sistema
            webbrowser.open(f"file://{os.path.abspath(filepath)}")

        except Exception as ex:
            self.log.info(f"Error al intentar actualizar la grafica:{ex}")
            self.log.error(f"Error al intentar actualizar la grafica: {ex}")
            return None
