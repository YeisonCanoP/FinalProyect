
import flet as ft
#Clase para manejjar la configuracion inicial que debe tener la pagina
class PageConfig:
    @staticmethod
    def configure(page):
        page.title = "Vizora"
        page.fonts = {
            "NotoSans": "fonts/NotoSans/NotoSans-VariableFont_wdth,wght.ttf",
            "Poppins": "fonts/Poppins/Poppins-Regular.ttf",
            "PoppinsBold": "fonts/Poppins/Poppins-Bold.ttf",
        }
        page.theme = ft.Theme(
            font_family="Poppins",
        )
        page.padding = 0
        page.expand = True