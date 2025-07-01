import asyncio
import flet as ft
import sys
sys.path.append('c:/Users/yeiso/OneDrive/Escritorio/Proyecto/final_proyect')
from app.utils.logger import Logger
from app.utils.utils import Utils

#Builder para crear elementos ahorrar tiempo y codigo
class Builder:

    def __init__(self):
        self.log = Logger("app/logs/builder.log").get_logger()
        self.colorLetra = "#0D0630"
        self.fondo = "#f5f5f5"

    #Funcion para crear un tooltip
    def create_tooltip(self, text:str,vertical_offset:int=25) -> ft.Tooltip:
        tooltip = ft.Tooltip(
            message=text,
            bgcolor=self.colorLetra,
            border_radius=10,
            text_style=ft.TextStyle(
                color=ft.Colors.WHITE,
                size=11,
                font_family="Poppins",
                weight=ft.FontWeight.W_500,
                letter_spacing=1,
            ),
            vertical_offset=vertical_offset,
            wait_duration=550
        )

        return tooltip

    #Funcion para crear un texfield
    def create_textfield(self,password:bool,hint_text:str,prefix_icon:ft.Icon) -> ft.TextField:
        texfield = ft.TextField(
            autofocus=True,
            bgcolor=self.fondo,
            border_color=ft.Colors.TRANSPARENT,
            border_radius=10,
            password=password,
            can_reveal_password=password,
            color=self.colorLetra,
            content_padding=ft.padding.all(8),
            hint_text=hint_text,
            text_style=ft.TextStyle(
                color=self.colorLetra,
                size=14,
                weight=ft.FontWeight.W_500,
            ),
            hint_style=ft.TextStyle(
                color=ft.Colors.GREY_400,
                size=14,
                weight=ft.FontWeight.W_500
            ),
            prefix_icon=prefix_icon,
        )

        return texfield
    
    #Funcion para crear un boton
    def create_button(self,tamañoText:str,bgcolor:str,text:str,on_click:None,radius:int=20,col = None,hover=None) -> ft.ElevatedButton:
        boton=ft.ElevatedButton(
            text=text,
            expand=True,
            bgcolor=bgcolor,
            on_hover=hover,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                padding=ft.padding.only(top=3, bottom=3, left=20, right=20),
                shape=ft.RoundedRectangleBorder(radius=radius),
                text_style=ft.TextStyle(
                    color="white",
                    size=tamañoText,
                    weight=ft.FontWeight.W_500,
                    letter_spacing=1.5,
                ),
            ),
            on_click=on_click,
        )

        return boton
    
    #Funcion para crear un iconButton
    def create_icon_button(self,icon:ft.Icon,tooltip:ft.Tooltip,size:int,colorIcon:str,bgcolor:str,offset,on_click) -> ft.IconButton:
        icon_button = ft.IconButton(
            alignment=ft.alignment.center,
            icon=icon,
            icon_color=colorIcon,
            icon_size=size,
            tooltip=self.create_tooltip(tooltip,offset),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=20),
                padding=ft.padding.all(10),
                bgcolor=bgcolor,
            ),
            on_hover=lambda e:Utils().on_hover(e),
            on_click=on_click,

        )

        return icon_button
    
    #Funcion para crear dropdown
    def create_dropdown(self,ref,options:list,onchange) -> ft.Dropdown:
        dropdown = ft.Dropdown(
            ref=ref,
            options=options,
            expand=True,
            value="7",
            border_radius=25,
            border_color=ft.Colors.TRANSPARENT,
            bgcolor=self.colorLetra,
            color=self.colorLetra,
            text_style=ft.TextStyle(
                color=self.colorLetra,
                size=14,
                weight=ft.FontWeight.W_500
            ),
            hint_text="Seleccione una opción",
            hint_style=ft.TextStyle(
                color=ft.Colors.GREY_400,
                size=12,
                weight=ft.FontWeight.W_500
            ),
            on_change=onchange
        )

        return dropdown

    #Funcion para crear el SnackBar con la alerta 
    def crearSnackBar(self,e,texto:str,tipo:str = "success"):
        #Creo el snakcbar
        snackBar= ft.SnackBar(
            content=ft.Text(
                f"{texto}",
                style=ft.TextStyle(
                    color="white" if tipo == "success" else ft.Colors.RED,
                    font_family="Poppins",
                    size=15,
                    weight=ft.FontWeight.W_500,
                ),
            ),
            elevation=0,
            action="Aceptar",
            action_color="white",
            bgcolor="#0D0630" if tipo == "success" else ft.Colors.with_opacity(0.7, ft.Colors.WHITE),
            duration=3000,
            margin=ft.margin.only(top=10),
        )

        e.page.open(snackBar)
        e.page.update()