import asyncio
import flet as ft
import sys


sys.path.append('c:/Users/yeiso/OneDrive/Escritorio/Proyecto/final_proyect')
from app.utils.logger import Logger
from app.utils.builder import Builder
from app.utils.utils import Utils
from app.core.login import LogicLogin

#Clase para menjar al creacion del login en flet Vizora 
class ViewLogin():
    
    #Construcot de la clase }
    def __init__(self, page: ft.Page):
        """
        Constructor de la clase ViewLogin.
        Inicializa la página y establece el título.
        """
        self.refContainerGoogle = ft.Ref[ft.Container]()
        self.refContainerEncabezado = ft.Ref[ft.Container]()
        self.refTitulo = ft.Ref[ft.Text]()
        self.refContainerCuerpo = ft.Ref[ft.Container]()
        self.refTituloGoogle = ft.Ref[ft.Text]()
        self.refTexfieldUser = ft.Ref[ft.Container]()
        self.refTexfieldPassword = ft.Ref[ft.Container]()
        self.refErrorLogin = ft.Ref[ft.Container]()
        self.refBotonLogin = ft.Ref[ft.Container]()
        self.imagen_fondo ="https://techwebgato.s3.us-east-1.amazonaws.com/imagenes/fondoLoginD.webp"
        self.icono_google = "https://techwebgato.s3.us-east-1.amazonaws.com/imagenes/icono_google.svg"
        self.log = Logger("/app/logs/viewLogin.log").get_logger()
        self.colorLetra = "#0D0630"
        self.page = page
        self.builder = Builder()
    
    #Funcion  para crear el container de fondo
#Funcion para crear el fondo del login
    def crear_fondo(self):
        fondo = ft.ResponsiveRow(
            expand=True,
            controls=[
            # Container o imagen de fondo
            ft.Container(
                width=float("inf"),
                height=float("inf"),
                expand=True,
                content=ft.Image(
                    src=self.imagen_fondo,
                    expand=True,
                    fit=ft.ImageFit.FILL,
                ),
            ),
            ]
        )
        return fondo

    #Funcion para crear el encabezado del contianer de login
    def create_encabezado(self):
        encabezado = ft.ResponsiveRow(
            expand=True,
            controls=[
                #Container del encabezado
                ft.Container(
                    expand=True,
                    alignment=ft.alignment.bottom_center,
                    content=ft.Text(
                        "Bienvenido a Vizora",
                        style=ft.TextStyle(
                            size=27,
                            color=self.colorLetra,
                            letter_spacing=2,
                            weight=ft.FontWeight.W_900,
                            font_family="Poppins",
                        ),
                        ref=self.refTitulo
                    )
                ),
            ]
        )

        return encabezado
    
    #Funcion para crear el cuerpo, donde va estar los texfields y etc
    def create_cuerpo(self):
        from app.modules.login.logic.logic import LogicViewLogin
        cuerpo = ft.ResponsiveRow(
            expand=True,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Column(
                    expand=True,
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=33,
                    col ={"xs":9,"sm":7.5,"md":7.5,"lg":6,"xl":5.5,"xxl":6},
                    controls=[
                        #Container del texfield de usuario
                        ft.Container(
                            alignment=ft.alignment.center,
                            height=40,
                            ref=self.refTexfieldUser,
                            content=self.builder.create_textfield(
                                password=False,
                                hint_text="Ingrese su correo",
                                prefix_icon=ft.Icons.PERSON
                            ),
                        ),
                        #Container del texfield de contraseña
                        ft.Container(
                            alignment=ft.alignment.top_center,
                            height=40,
                            ref=self.refTexfieldPassword,
                            content=self.builder.create_textfield(
                                password=True,
                                hint_text="Ingrese su contraseña",
                                prefix_icon=ft.Icons.LOCK
                            ),
                        ),
                        #Container del boton de login
                        ft.Container(
                            margin=ft.margin.only(top=0),
                            height=40,
                            ref=self.refBotonLogin,
                            content=self.builder.create_button(
                                tamañoText=15,
                                bgcolor=self.colorLetra,
                                text="Iniciar Sesión",
                                on_click=lambda e: asyncio.run(LogicViewLogin(self).iniciar_sesion(e)),
                                hover= lambda e:Utils().on_hover(e, scale=1.05)
                            )
                        ),
                    ]
                )
            ]
        )

        return cuerpo

    #Funcion para crear el pie del container, en este caso sera donde este el logo de inciar con google
    def create_pie(self):
        pie = ft.Container(
            bgcolor="white",
            ref=self.refContainerGoogle,
            on_hover=lambda e: Utils().on_hover(e, scale=1.1),
            col = {"xs":8,"sm":8,"md":5.3,"lg":5.3,"xl":5.6,"xxl":5},
            padding=ft.padding.only(left=10, right=10),
            border_radius=15,
            on_click=lambda e: asyncio.run(LogicLogin().login_google(e)),
            content=ft.ResponsiveRow(
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
                controls=[
                    #Contianer ocn el texto
                    ft.Container(
                        alignment=ft.alignment.center,
                        col = {"xs":10,"sm":10,"md":10,"lg":10,"xl":10,"xxl":10},
                        content=ft.Text(
                            "Continuar con Google",
                            style=ft.TextStyle(
                                size=13.5,
                                color=self.colorLetra,
                                weight=ft.FontWeight.W_900,
                                font_family="Poppins"
                            ),
                            ref=self.refTituloGoogle,
                            text_align=ft.TextAlign.CENTER,
                        )
                    ),
                    #Icon de google
                    ft.Container(
                        col = {"xs":2,"sm":2,"md":2,"lg":2,"xl":2,"xxl":2},
                        alignment=ft.alignment.center,
                        content=ft.Image(
                            src=self.icono_google,
                            width=25,
                            height=25,
                        )
                    ),
                ]
            )
        )

        responsi = ft.ResponsiveRow(
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True,
            controls=[
                pie
            ]
        )

        return responsi

    #Funcion para crear lo que tendra dentro el container, estara divido en encabezado, cuerpo y pie
    def create_contenido(self):
        container = ft.Column(
            expand=True,
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                #Container de encabezado
                ft.Container(
                    height=None,
                    margin=ft.margin.only(top=10),
                    alignment=ft.alignment.center,
                    ref=self.refContainerEncabezado,
                    content=self.create_encabezado()
                ),
                #Container del cuerpo
                ft.Container(
                    height=None,
                    ref=self.refContainerCuerpo,
                    content=self.create_cuerpo()
                ),
                #Container del pie
                ft.Container(
                    content=self.create_pie()
                )
            ]
        )
        return container

    #Funcion para crear el container que va tener el login y todo la informacion del login
    def create_container(self):
        container = ft.ResponsiveRow(
            expand=True,
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                #Columnna que va tener el container del login con los otros dos contenedore para hacer espacio
                ft.Column(
                    expand=True,
                    alignment=ft.MainAxisAlignment.CENTER,
                    col ={"xs":9,"sm":7.5,"md":7.5,"lg":6,"xl":4.5,"xxl":4},
                    controls=[
                        ft.Container(
                            expand=3,
                            alignment=ft.alignment.center,
                        ),
                        ft.Stack(
                            alignment=ft.alignment.center,
                            expand=8,
                            controls=[
                                ft.Container(
                                    alignment=ft.alignment.center,
                                    gradient=ft.LinearGradient(
                                        begin=ft.alignment.bottom_left,
                                        end=ft.alignment.top_right,
                                        colors=["white","white","#FDF0EA","#FCF3EE","#EFE3DF"]
                                    ),
                                    opacity=0.4,
                                    border_radius=25,
                                ),
                                self.create_contenido()
                            ]
                        ),
                        ft.Container(
                            expand=3,
                            alignment=ft.alignment.center,
                        )
                    ]
                ),
            ]
        )
    
        return container

    #Funcion para crear el login
    def create_login(self):
        self.log.info("Creating login view")

        fondo_contenido=ft.Stack(
            expand=True,
            alignment=ft.alignment.center,
            controls=[
                # Fondo del login
                self.crear_fondo(),
                ft.Container(
                    bgcolor=ft.Colors.TRANSPARENT,
                    expand=True,
                    alignment=ft.alignment.center,
                    content=self.create_container()
                )
            ]
        )

        return ft.View(
            "/",
            controls=[fondo_contenido],
            padding=0,
        )
