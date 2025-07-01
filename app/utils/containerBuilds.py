import flet as ft
import sys
sys.path.append('c:/Users/yeiso/OneDrive/Escritorio/Proyecto/final_proyect')
from app.utils.utils import Utils

# clase para manejar la creacion de container predefinidos
class ContainerBuilds:
    def __init__(self,page):
        self.colorLetra = "#0D0630"
        self.refConInformacion_Titulo = ft.Ref[ft.Text]()
        self.refConInformacion_Subtitulo = ft.Ref[ft.Text]()
        self.refConInformacion_Cantidad = ft.Ref[ft.Text]()
        self.page = page

    def crear_containerTablero(self,titulo: str, subtitulo: str, cantidad: str,extra:bool=False) -> ft.Container:
        #Containe rpredifnido para crear el conteneido de informacion simple de la parte de tablero
        container = (
            ft.Container(
                bgcolor="white",
                padding=ft.padding.only(left=25, right=25, top=15, bottom=15),
                col={"xs": 12, "sm": 6, "md": 6, "lg": 2.7, "xl": 2.9, "xxl": 2.7} if not extra else {"xs": 12, "sm": 12, "md": 6, "lg": 2.7, "xl": 2.9, "xxl": 2.7},
                border_radius=25,
                shadow=ft.BoxShadow(
                    color=ft.Colors.BLACK26,
                    blur_radius=11,
                    spread_radius=0,
                    offset=ft.Offset(0, 5)
                ),
                on_hover=lambda e: Utils().on_hover(e,
                                                    scale=1.08,
                                                    colorOrginal="white",
                                                    colorCambiar=self.colorLetra,
                                                    letras=[
                                                        self.refConInformacion_Titulo,
                                                        self.refConInformacion_Subtitulo,
                                                        self.refConInformacion_Cantidad
                                                    ]
                                                    ),
                content=ft.Column(
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.START,
                    spacing=10,
                    controls=[
                        # Colimn con el titulo y subtitulo
                        ft.Column(
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.START,
                            spacing=0,
                            controls=[
                                # Texto que va decir el titulo de ventas por dia
                                ft.Text(
                                    f"{titulo}",
                                    style=ft.TextStyle(
                                        size=18 if self.page.width > 600 else 19,
                                        color=self.colorLetra,
                                        letter_spacing=1,
                                        font_family="Poppins",
                                        weight=ft.FontWeight.W_900,
                                        height=1.2
                                    ),
                                    text_align=ft.TextAlign.START,
                                    ref=self.refConInformacion_Titulo
                                ),
                                # Subtitulo
                                ft.Text(
                                    f"{subtitulo}",
                                    style=ft.TextStyle(
                                        size=11.3 if self.page.width > 600 else 12,
                                        color=self.colorLetra,
                                        letter_spacing=1,
                                        weight=ft.FontWeight.W_300,
                                    ),
                                    text_align=ft.TextAlign.START,
                                    ref=self.refConInformacion_Subtitulo
                                ),
                            ],
                        ),
                        # Texto que va decir el total de ventas del dia
                        ft.Text(
                            f"{cantidad}",
                            style=ft.TextStyle(
                                size=25 if self.page.width > 600 else 22,
                                color=self.colorLetra,
                                letter_spacing=1.5,
                                weight=ft.FontWeight.W_800,
                            ),
                            text_align=ft.TextAlign.START,
                            ref=self.refConInformacion_Cantidad
                        )
                    ],
                )
            )
        )

        return container
