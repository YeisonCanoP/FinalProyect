from datetime import datetime
import flet as ft
import asyncio
import sys
import warnings

from app.utils.sessionManager import SessionManager

warnings.filterwarnings("ignore", category=DeprecationWarning)
sys.path.append("c:/Users/yeiso/OneDrive/Escritorio/Proyecto/final_proyect")
from app.utils.logger import Logger
from app.utils.builder import Builder
from app.utils.containerBuilds import ContainerBuilds
from app.core.login import LogicLogin
from app.modules.vtgier.consulta import Vtiger
from app.modules.analisis.analisisContainer import AnalisisContainer
from app.modules.analisis.graficaLineal import GraficaLineal
from app.modules.analisis.graficaPastel import GraficaPastel

# Clase para manejar la construccion de la vista de tablero
class ViewTablero:
    def __init__(self, page):
        self.page = page
        self.colorLetra = "#090325"
        self.perfil = SessionManager.get_user(page)[0]
        self.refContainerEncabezado = ft.Ref[ft.Container]()
        self.refEncabezadoTitulo = ft.Ref[ft.Text]()
        self.refEncabezadoSubtitulo = ft.Ref[ft.Text]()
        self.refContainerCuerpo = ft.Ref[ft.Container]()
        self.refTituloGraficaPastel = ft.Ref[ft.Text]()
        self.refGraficaPastel = ft.Ref[ft.Container]()
        self.refColumnaGraficaProductividad = ft.Ref[ft.Column]()
        self.refDropdownGraficaProductividad = ft.Ref[ft.Dropdown]()
        self.refContainerFooter = ft.Ref[ft.Container]()
        self.log = Logger("app/logs/viewTablero.log").get_logger()
        self.vtiger = Vtiger()
        self.analisiContainer = AnalisisContainer()
        self.graficaLineal = GraficaLineal(self)
        self.graficaPastel = GraficaPastel(self)

    # Funcion para crear el encabezado del tablero
    def create_encabezado(self):
        try:
            content = ft.ResponsiveRow(
                expand=True,
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    # Texto del encabezado
                    ft.Column(
                        alignment=ft.MainAxisAlignment.START,
                        horizontal_alignment=ft.CrossAxisAlignment.START,
                        col={
                            "xs": 8,
                            "sm": 9,
                            "md": 8,
                            "lg": 8,
                            "xl": 9.3,
                            "xxl": 9.3,
                        },
                        spacing=5,
                        controls=[
                            ft.Text(
                                "DASHBOARD",
                                style=ft.TextStyle(
                                    size=25,
                                    color=self.colorLetra,
                                    letter_spacing=1,
                                    weight=ft.FontWeight.W_900,
                                ),
                                text_align=ft.TextAlign.START,
                                ref=self.refEncabezadoTitulo,
                            ),
                            # Luego el subtitulo
                            ft.Text(
                                "Resumen operativo y financiero de la empresa",
                                style=ft.TextStyle(
                                    size=14,
                                    color=self.colorLetra,
                                    letter_spacing=1.3,
                                    weight=ft.FontWeight.W_400,
                                ),
                                text_align=ft.TextAlign.START,
                                ref=self.refEncabezadoSubtitulo,
                            ),
                        ],
                    ),
                    # Fecha y hora actual
                    ft.Container(
                        alignment=ft.alignment.center,
                        col={
                            "xs": 6,
                            "sm": 3,
                            "md": 2,
                            "lg": 2,
                            "xl": 1.5,
                            "xxl": 1.5,
                        },
                        content=ft.Text(
                            f"{datetime.now().strftime("%d/%m/%Y")}",
                            style=ft.TextStyle(
                                size=17,
                                color=self.colorLetra,
                                letter_spacing=1.3,
                                weight=ft.FontWeight.W_400,
                            ),
                            text_align=ft.TextAlign.START,
                        ),
                    ) if self.page.width > 600 else ft.Container(visible=False),
                    # IconBoton de salir o de cerrar sesion
                    ft.Container(
                        alignment=ft.alignment.center,
                        col={
                            "xs": 2,
                            "sm": 1.5,
                            "md": 1,
                            "lg": 1,
                            "xl": 0.6,
                            "xxl": 0.6,
                        },
                        content=Builder().create_icon_button(
                            icon=ft.Icons.LOGOUT,
                            tooltip="Cerrar sesión",
                            size=27 if self.page.width > 600 else 23,
                            colorIcon="white",
                            bgcolor=self.colorLetra,
                            offset=30,
                            on_click=lambda e: asyncio.run(LogicLogin().logout(e)),
                        ),
                    ),
                    # Boton para colocar la imagen del ususario en caso de que tenga
                    ft.Container(
                        alignment=ft.alignment.center,
                        col={
                            "xs": 2,
                            "sm": 1.5,
                            "md": 1,
                            "lg": 1,
                            "xl": 0.6,
                            "xxl": 0.6,
                        },
                        content=Builder().create_icon_button(
                            icon=ft.Icons.PERSON,
                            tooltip=f"{self.perfil}" if self.perfil else "Perfil",
                            size=27 if self.page.width > 600 else 23,
                            colorIcon="white",
                            bgcolor=self.colorLetra,
                            offset=30,
                            on_click=None,
                        ),
                    ),
                ],
            )

            return content

        except Exception as ex:
            self.log.error(f"Error creating header: {ex}")
            raise ex

    # Funcion para crear los container de informacion basica
    def create_container_informacion(self):
        try:
            # Crear el array de contenedores de informacion basica
            container = [
                # Primer container
                ContainerBuilds(self.page).crear_containerTablero(
                    titulo="INGRESO DIARIO" if self.page.width > 600 else "INGRESO \nDIARIO",
                    subtitulo="Ganancias generadas durante el día",
                    cantidad=f"${self.analisiContainer.ingresosDiarios}" if self.analisiContainer.ingresosDiarios else "$0",
                ),
                # Segundo container
                ContainerBuilds(self.page).crear_containerTablero(
                    titulo="INGRESO MENSUAL",
                    subtitulo="Ganancias generadas durante el mes",
                    cantidad=f"${self.analisiContainer.ingresosMensuales}" if self.analisiContainer.ingresosMensuales else "$0",
                ),
                # Tercer container
                ContainerBuilds(self.page).crear_containerTablero(
                    titulo="CLIENTES NUEVOS",
                    subtitulo="Clientes que se han registrado hoy",
                    cantidad=f"{self.vtiger.newClients}",
                ),
                # Facturas generadas
                ContainerBuilds(self.page).crear_containerTablero(
                    titulo="FACTURAS GENERADAS",
                    subtitulo="Facturas emitidas durante el día",
                    cantidad=f"{self.analisiContainer.totalFacturas}" if self.analisiContainer.totalFacturas else "0",
                ),
            ]

            return container

        except Exception as ex:
            self.log.error(f"Error creating basic information container: {ex}")
            raise ex

    # Funcion para crear la grafica de prodcutvidad
    def create_grafica_productividad(self):
        try:
            # Estoe s temoral esta sera la grafica de error
            grafica = self.graficaLineal.grafica

            # Container de la grafica de linea de productividad
            container = ft.Container(
                padding=ft.padding.only(left=20, right=20, top=10, bottom=10),
                bgcolor="white",
                expand=True,
                aspect_ratio=2 if self.page.width > 600 else 1,
                border_radius=20,
                shadow=ft.BoxShadow(
                    color=ft.Colors.BLACK26,
                    blur_radius=11,
                    spread_radius=0,
                    offset=ft.Offset(0, 5)
                ),
                col={"xs": 12, "sm": 12, "md": 12, "lg": 6, "xl": 6, "xxl": 6},
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.START,
                    expand=True,
                    scroll=ft.ScrollMode.AUTO,
                    auto_scroll= True,
                    spacing=10,
                    controls=[
                        # Titulo de la grafica y boton de expandir
                        ft.ResponsiveRow(
                            alignment=ft.MainAxisAlignment.START,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=10,
                            controls=[
                                # Titulo de la grafica
                                ft.Text(
                                    "GRÁFICA DE PRODUCTIVIDAD",
                                    style=ft.TextStyle(
                                        size=18,
                                        color=self.colorLetra,
                                        letter_spacing=1,
                                        weight=ft.FontWeight.W_900,
                                    ),
                                    col={
                                        "xs": 12,
                                        "sm": 5,
                                        "md": 6,
                                        "lg": 7,
                                        "xl": 7,
                                        "xxl": 7,
                                    },
                                    expand=True,
                                    text_align=ft.TextAlign.START,
                                ),
                                ft.Container(
                                    col={"xs": 8,"sm": 5,"md": 6,"lg": 4,"xl": 4,"xxl": 4},
                                    content=Builder().create_dropdown(
                                        ref=self.refDropdownGraficaProductividad,
                                        options=[
                                            ft.dropdown.Option(
                                                "7","7 días",
                                                text_style=ft.TextStyle(
                                                    size=14,
                                                    color="white",
                                                    weight=ft.FontWeight.W_500,
                                                    font_family="Poppins"
                                                ),
                                            ),
                                            ft.dropdown.Option(
                                                "30","30 días",
                                                text_style=ft.TextStyle(
                                                    size=14,
                                                    color="white",
                                                    weight=ft.FontWeight.W_500,
                                                    font_family="Poppins"
                                                ),
                                            ),
                                            ft.dropdown.Option(
                                                "90","90 días",
                                                text_style=ft.TextStyle(
                                                    size=14,
                                                    color="white",
                                                    weight=ft.FontWeight.W_500,
                                                    font_family="Poppins"
                                                ),
                                            ),
                                            ft.dropdown.Option(
                                                "mes","Mes",
                                                text_style=ft.TextStyle(
                                                    size=14,
                                                    color="white",
                                                    weight=ft.FontWeight.W_500,
                                                    font_family="Poppins"
                                                ),
                                            ),
                                            ft.dropdown.Option(
                                                "anio","Año",
                                                text_style=ft.TextStyle(
                                                    size=14,
                                                    color="white",
                                                    weight=ft.FontWeight.W_500,
                                                    font_family="Poppins"
                                                ),
                                            ),
                                        ],
                                        onchange=lambda _: asyncio.run(self.graficaLineal.actualizar_grafica(self.refDropdownGraficaProductividad.current.value))
                                    ),
                                ),
                                # Icon buton
                                ft.Container(
                                    alignment=ft.alignment.center_right,
                                    col={
                                        "xs": 4,
                                        "sm": 2,
                                        "md": 6,
                                        "lg": 1,
                                        "xl": 1,
                                        "xxl": 1,
                                    },
                                    content=Builder().create_icon_button(
                                        icon=ft.Icons.ARROW_OUTWARD_ROUNDED,
                                        tooltip="Expandir gráfica",
                                        size=20,
                                        colorIcon="white",
                                        bgcolor=self.colorLetra,
                                        offset=30,
                                        on_click=lambda e: asyncio.run(self.graficaLineal.mostrar_graficaEnWeb(web=True,e=e)),
                                    ),
                                ),
                            ],
                        ),
                        # grafica de linea de productividad
                        ft.Container(
                            grafica,
                            ref=self.refColumnaGraficaProductividad,
                        ) if self.page.width > 512  else ft.Container(visible=False),
                    ],
                ),
            )

            return container

        except Exception as ex:
            self.log.error(f"Error creating productivity graph: {ex}")
            raise ex

    # Funcin para crear la grafica de pastel
    def create_grafica_pastel(self):
        try:
            # Esto sera por el momento, es la grafica de error
            # Estoe s temoral esta sera la grafica de error
            grafica = self.graficaPastel.grafica

            container = ft.Container(
                padding=ft.padding.only(left=20, right=20, top=16, bottom=10),
                bgcolor="white",
                border_radius=20,
                aspect_ratio=0.965 if self.page.width > 500 else 1.2,
                shadow=ft.BoxShadow(
                    color=ft.Colors.BLACK26,
                    blur_radius=11,
                    spread_radius=0,
                    offset=ft.Offset(0, 5)
                ),
                col={"xs": 12, "sm": 6, "md": 6, "lg": 6, "xl": 3, "xxl": 3},
                content=ft.Column(
                    alignment=ft.MainAxisAlignment.START,
                    horizontal_alignment=ft.CrossAxisAlignment.START,
                    scroll=ft.ScrollMode.AUTO,
                    spacing=10,
                    controls=[
                        # Primer con el titulo de la grafica
                        ft.Text(
                            "VENTAS POR PRODUCTO",
                            style=ft.TextStyle(
                                size=18,
                                color=self.colorLetra,
                                letter_spacing=1,
                                weight=ft.FontWeight.W_900,
                            ),
                            text_align=ft.TextAlign.START,
                        ),
                        #Texto que idnica si es por mes o por año
                        ft.Text(
                            "Mes" if self.page.width > 600 else "Mes",
                            style=ft.TextStyle(
                                size=14,
                                color=self.colorLetra,
                                letter_spacing=1.3,
                                weight=ft.FontWeight.W_400,
                            ),
                            ref=self.refTituloGraficaPastel,
                            text_align=ft.TextAlign.START,
                        ),
                        #responsive row con la grafica de pastel
                        ft.Container(
                            grafica,
                            ref=self.refGraficaPastel,
                        )
                    ],
                ),
            )

            return container
        except Exception as ex:
            self.log.error(f"Error creating pie chart: {ex}")
            raise ex

    #Funcion para crear container para cosas extra
    def create_container_extra(self):
        try:
            # Crear un container extra para cosas que se necesiten
            container = ft.Container(
                padding=ft.padding.all(20) if self.page.width > 600 else ft.padding.all(15),
                border_radius=20,
                aspect_ratio=0.961,
                col={"xs": 12, "sm": 6, "md": 6, "lg": 6, "xl": 3, "xxl": 3},
                content=ft.Column(
                    alignment=ft.MainAxisAlignment.START,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    expand=True,
                    scroll=ft.ScrollMode.AUTO,
                    spacing=20,
                    controls=[
                        ft.Container(
                            expand=True,
                            padding=ft.padding.only(left=25, right=25, top=15, bottom=10) if self.page.width > 600 else ft.padding.all(15),
                            content=ContainerBuilds(self.page).crear_containerTablero(
                                titulo="PRODUCTOS EN STOCK",
                                subtitulo="Productos disponibles en inventario",
                                cantidad=f"{self.vtiger.cantidadProductos}",
                                extra=True,
                            ),
                        ),
                        ft.Container(
                            padding=ft.padding.only(left=25, right=25, top=10, bottom=30) if self.page.width > 600 else ft.padding.all(15),
                            content=ContainerBuilds(self.page).crear_containerTablero(
                                    titulo="COTIZACIONES",
                                    subtitulo="Cotizaciones que esperan respuesta",
                                    cantidad=f"{self.vtiger.cotizaciones}",
                                    extra=True,
                                ),
                        ),
                        ft.Container(
                            padding=ft.padding.only(left=25, right=25, top=10, bottom=30) if self.page.width > 600 else ft.padding.all(15),
                            content=ContainerBuilds(self.page).crear_containerTablero(
                                    titulo="TRANSPORTE",
                                    subtitulo="Ingresos generados por transporte de productos",
                                    cantidad=f"{self.analisiContainer.transporteMes}" if self.analisiContainer.ingresosDiarios else "$0",
                                    extra=True,
                                ),
                        ),
                    ]
                ), 
            )

            return container

        except Exception as ex:
            self.log.error(f"Error creating extra container: {ex}")
            raise ex

    # Funcion para crear la zona donde van estar las graficas y la pastel
    def create_graficas(self):
        try:
            # Aqui se pueden crear las graficas y tablas que se necesiten
            graficas = [
                self.create_grafica_productividad(),
                # Aui va la grafica pastel
                self.create_grafica_pastel(),
                # Aqui va el container extra que se necesite
                self.create_container_extra(),
            ]

            return graficas

        except Exception as ex:
            self.log.error(f"Error creating graphs and tables area: {ex}")
            raise ex

    # Funcion para crear el conteneido del cuerpo del tablero
    def create_cuerpo(self):
        try:
            # Dentro de cuerpo tamien se va dividr en column, una donde va estar todo los container
            # En la segunda column va estar las graficas y tablas
            column = ft.Column(
                alignment=ft.MainAxisAlignment.START,
                expand=True,
                spacing=30,
                controls=[
                    # Primer responsive row donde va estar los contenedores de informacion
                    ft.ResponsiveRow(
                        alignment=ft.MainAxisAlignment.START,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=40,
                        run_spacing=30,
                        controls=self.create_container_informacion(),
                    ),
                    # Seugno responsive row donde va estar las graficas y tablas
                    ft.ResponsiveRow(
                        alignment=ft.MainAxisAlignment.START,
                        expand=True,
                        spacing=20,
                        run_spacing=30,
                        controls=self.create_graficas(),
                    ),
                ],
            )

            return column

        except Exception as ex:
            self.log.error(f"Error creating body content: {ex}")
            raise ex

    # Funcion para crear el cotnendido, el encabezado, el contenido y el footer del tablero
    def create_pagina(self):
        try:
            # Crear el ccolumn que va tener todo eso
            column = ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
                expand=True,
                scroll=ft.ScrollMode.AUTO,
                controls=[
                    # Primero creo entonces el encabezado
                    ft.Container(
                        expand=2,
                        ref=self.refContainerEncabezado,
                        padding=ft.padding.only(left=20, right=20, top=10, bottom=10),
                        content=self.create_encabezado(),
                    ),
                    # Luego creo el contenido
                    ft.Container(
                        expand=15,
                        ref=self.refContainerCuerpo,
                        padding=ft.padding.only(left=20, right=20, top=10, bottom=10),
                        content=self.create_cuerpo(),
                    ),
                ],
            )

            return column

        except Exception as ex:
            self.log.error(f"Error creating page: {ex}")
            raise ex

    def create_tablero(self):
        try:
            container = ft.Container(
                padding=ft.padding.all(25),
                margin=0,
                expand=True,
                bgcolor="#FFFAF0",
                content=self.create_pagina(),
            )

            return ft.View(
                "/tablero",
                controls=[container],
                padding=0,
            )

        except Exception as ex:
            self.log.error(f"Error creating tablero view: {ex}")
            raise ex

