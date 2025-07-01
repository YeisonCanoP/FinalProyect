import sys
import flet as ft
import asyncio
import pandas as pd
import random
sys.path.append("c:/Users/yeiso/OneDrive/Escritorio/Proyecto/App-Inventario")
from app.modules.analisis.querys.facturas import Query_Facturas
from utils.singleton import SingletonMeta
from app.utils.logger import Logger
from app.utils.utils import Utils

class GraficaPastel(metaclass=SingletonMeta):

    def __init__(self,view):
        self.view = view
        self.page = view.page
        self.logger = Logger("app/logs/Graficas.log").get_logger()
        self.grafica = None
        self.colorLetra = "#0D0630"
        self.textoInfo = "Mes"
        self.colores = [
            "#D9705A",  # Naranja suave
            "#F7A13E",  # Naranja cálido
            "#F9C8A4",  # Durazno
            "#D45A58",  # Rojo cálido
            "#F07F7F",  # Rosa coral
        ]
        self.coloresProductos = [
            "#4A90E2",  # Azul brillante  
            "#6EC1E4",  # Celeste  
            "#A0D2DB",  # Azul pastel  
            "#87A8D0",  # Azul grisáceo  
            "#B5C7E3",  # Azul claro frío  
        ]

    #Funcion para selecionar los colores de la grafica
    def seleccionar_colores(self,colores):
        coloresLista = random.sample(colores, 5)
        return coloresLista

    #Funcion para obtener los datos para la grafica pastel
    async def obtener_datos(self,tipo="mes"):
        try: 
            #Si el tipo es mes o anual se obtiene los datos de la base de datos
            if tipo == "mes":
                #Obtengo los datos de la base de datos
                datos = await Query_Facturas().traer_productos_mas_vendidosMes()

            elif tipo == "anio":
                #Obtengo los datos de la base de datos
                datos = await Query_Facturas().traer_productos_mas_vendidosAnio()

            else:
                return None

            #Si los datos son None se return
            if not datos:
                self.logger.info("No se encontraron datos para la gráfica pastel.")
                self.logger.error("No se encontraron datos para la gráfica pastel.")
                return None
                
            #Se asginan los valores del column
            df=pd.DataFrame(datos, columns=["nombre","total_vendido","cantidad_vendida"])

            #Calcular el porcentaje de ventas
            df['porcentaje'] = (df['total_vendido'] / df['total_vendido'].sum()) * 100

            #Redondeo los datos a 1 decimal
            df["porcentaje"] = df["porcentaje"].astype(float).round(1)

            return df
        except Exception as ex:
            self.logger.info(f"Error al obtener los datos para la grafica pastel: {str(ex)}")
            self.logger.error(f"Error al obtener los datos para la grafica pastel: {str(ex)}")
            return None

    #Fucnion para crear la grafica pastel
    async def crear_pastel(self,tipo):
        try:
            df = await self.obtener_datos(tipo)
            #Si los datos son None se return
            if df is None or df.empty:
                self.logger.info("No se encontraron datos para la gráfica pastel.")
                await self.mostrar_graficaVacia()
                return 
            
            #Borde de la grafica
            normal_border = ft.BorderSide(0, ft.Colors.with_opacity(0, ft.Colors.WHITE))

            #Funcion para el evento de la grafica
            def on_chart_event(e: ft.PieChartEvent):
                if e.section_index is not None:
                    section = grafica.sections[e.section_index]
                    
                    if isinstance(section.data, tuple) and len(section.data) == 2:
                        productos, total_vendido = section.data
                        tooltip_text.value = f"{productos}: {Utils().formatNumero(total_vendido)}"
                        if tooltip_text.page is not None:
                            tooltip_text.update()

                        # 🔹 Ajusta el tamaño del sector al hacer hover
                    for idx, sec in enumerate(grafica.sections):
                        sec.radius = 90 if idx == e.section_index else 85
                    grafica.update()

            #tooltip de la grafica para colocar el nombre
            tooltip_text = ft.Text(
                "",
                style=ft.TextStyle(
                    font_family="Poppins",
                    size=12,
                    color=self.colorLetra,
                    weight=ft.FontWeight.W_500,
                    letter_spacing=0.5,
                ),
                text_align=ft.TextAlign.CENTER,
                expand=True,
            )

            #Colores
            if tipo == "mes":
                colores = self.seleccionar_colores(self.colores)
                self.textoInfo = "Mes"

            elif tipo == "anio":
                colores = self.seleccionar_colores(self.coloresProductos)
                self.textoInfo = "Año"

            #Se crea la grafica pastel
            grafica = ft.PieChart(
                    sections=[
                        ft.PieChartSection(
                            row["porcentaje"],
                            title=f"{row['porcentaje']}%",
                            title_position=0.7,
                            title_style=ft.TextStyle(
                                font_family="Poppins",
                                size=11,
                                color=self.colorLetra,
                                weight=ft.FontWeight.W_400,
                                italic=True,
                            ),
                            border_side=normal_border,
                            radius=85,
                            color=colores[i],
                            data=(row["nombre"], row["total_vendido"]),
                            )
                        for i,(_, row) in enumerate(df.iterrows())
                    ],
                    sections_space=0,
                    expand=True,
                    aspect_ratio=1.3,  
                    center_space_radius=0,  
                    on_chart_event=on_chart_event,
                )
            
            #Se crea el column para la grafica
            containerGrafica = ft.Column(
                expand=True,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
                controls=[
                    ft.Container(
                        expand=True,
                        alignment=ft.alignment.center,
                        content=tooltip_text,
                    ),
                    ft.Container(
                        expand=True,
                        alignment=ft.alignment.center,
                        content=grafica,
                    ),
                ]
            )

            #Sew remplaza por la variable de la clase
            self.grafica = containerGrafica

        except Exception as ex:
            self.logger.info(f"Error al crear la grafica pastel: {str(ex)}")
            self.logger.error(f"Error al crear la grafica pastel: {str(ex)}")
            return None
    
    #Funcion que se jeecutra cuando no hayan datos o no se pueda generar la grafica
    async def mostrar_graficaVacia(self):
        try:
            # Esto sera por el momento, es la grafica de error
            # Estoe s temoral esta sera la grafica de error
            grafica = ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
                expand=True,
                col={"xs": 12, "sm": 6, "md": 6, "lg": 6, "xl": 3, "xxl": 3},
                controls=[
                    # Titulo de la grafica
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
                            text_align=ft.TextAlign.CENTER,
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
            self.logger.info(f"Error al intentar mostrar la grafica:{ex}")
            self.logger.error(f"Error al intentar mostrar la grafica: {ex}")
            return None

    #Funcion para actualizar la grafica pastel
    async def actualizar_grafica(self, tipo):

        try:
            graficaPastel = self.view.refGraficaPastel.current
            textoInfo = self.view.refTituloGraficaPastel.current

            #Se crea la grafica pastel de nuevo con el nuevo tipo que se paso
            await self.crear_pastel(tipo)
            
            #Luego se acutaliza el conteneido de graficapastel en componentet
            graficaPastel.content = self.grafica


            #Se acutaliza el texto de informacion
            textoInfo.value = self.textoInfo

            textoInfo.update()

            #Luego se refresca la vista
            graficaPastel.update()

        except Exception as ex:
            self.logger.info(f"Error al actualizar la grafica pastel: {str(ex)}")
            self.logger.error(f"Error al actualizar la grafica pastel: {str(ex)}")
            return None