import asyncio
import flet as ft
import sys
sys.path.append('c:/Users/yeiso/OneDrive/Escritorio/Proyecto/final_proyect')
from app.utils.pageconfi import PageConfig
from app.utils.logger import Logger
from app.modules.login.interfaces.viewLogin import ViewLogin
from app.modules.panel.interfaces.viewTablero import ViewTablero
from app.modules.login.build.responsi import ResponsiLogin
from app.routers.fletFrontend import FletFrontendRouter
from app.modules.vtgier.consulta import Vtiger
from app.modules.analisis.analisisContainer import AnalisisContainer
from app.modules.analisis.graficaLineal import GraficaLineal
from app.modules.analisis.graficaPastel import GraficaPastel


log = Logger("app/logs/main.log").get_logger()

#Inicio en segundo plano de la aplicacion, la informacion de vtiger

#El nombre de la aplicacion es vizora
async def main(page: ft.Page):
    #Inicializacion la configuracion de la pagina
    PageConfig.configure(page)
    #Instancia de las vistas
    analisiscontainer= AnalisisContainer()
    view = ViewLogin(page)
    tablero = ViewTablero(page)
    graficalineal = GraficaLineal(tablero)
    graficaPastel = GraficaPastel(tablero)

    def aplicar_respondiHome():
        height = page.height
        responsi = ResponsiLogin(view)
        responsi.update_height(height)

    def page_resize(e):
        if page.route == "/":
            aplicar_respondiHome()

    def route_change(e):
        router = FletFrontendRouter(page, view, tablero)
        router.handle()


    page.on_route_change = route_change
    page.on_resized = page_resize
    page.go(page.route)
    page.update()
    await asyncio.sleep(0.2)
    asyncio.create_task(Vtiger()._init())
    asyncio.create_task(analisiscontainer.run())
    asyncio.create_task(graficalineal.mostrar_grafica(tipo="dias",dias=7))
    asyncio.create_task(graficaPastel.crear_pastel(tipo="mes"))

ft.app(target=main,view=ft.WEB_BROWSER,assets_dir="app/assets",port=52928)