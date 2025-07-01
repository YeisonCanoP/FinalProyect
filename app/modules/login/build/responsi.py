import sys
import flet as ft
sys.path.append('c:/Users/yeiso/OneDrive/Escritorio/Proyecto/final_proyect')
from app.modules.login.interfaces.viewLogin import ViewLogin
#Clase para traer todo los elementos que se deben adaptar a la pantalla
class ResponsiLogin:

    def __init__(self, view = ViewLogin(ft.Page)):
        self.page = view.page
        self.view = view
        self.refContainerGoogle = view.refContainerGoogle
        self.refContainerEncabezado = view.refContainerEncabezado
        self.refContainerCuerpo = view.refContainerCuerpo
        self.refTitulo = view.refTitulo
        self.refTituloGoogle = view.refTituloGoogle
        self.refTexfieldUser = view.refTexfieldUser
        self.refTexfieldPassword = view.refTexfieldPassword
        self.refBotonLogin = view.refBotonLogin

    #Funcion para actualizar dichos elementos
    def update_elements(self):
        self.refContainerEncabezado.current.update()
        self.refContainerCuerpo.current.update()
        self.refTitulo.current.update()

    #Funcion para actualizar los elementos del footer
    def update_heightFooter(self,height):
        width =self.page.width
        if height < 800:
            self.refTituloGoogle.current.size = 13.5
            if width > 600:
                self.refTituloGoogle.current.size = 14.5
            self.refContainerGoogle.current.height = height * 0.06
        elif height < 1000:
            self.refTituloGoogle.current.size = 13.5
            self.refContainerGoogle.current.height = height * 0.05
        elif height < 1200:
            self.refTituloGoogle.current.size = 14
            self.refContainerGoogle.current.height = height * 0.04
            if width > 1600:
                self.refTituloGoogle.current.size = 17
                self.refContainerGoogle.current.height = height * 0.046
        elif height < 1400:
            self.refTituloGoogle.current.size = 15
            self.refContainerCuerpo.current.height = height * 0.55

        self.refContainerGoogle.current.update()

    #Funcion para acutalizar el cuerpo de la pagina
    def update_heightCuerpo(self, height):
        width = self.page.width
        if width > 1400:
            self.refContainerCuerpo.current.height = height * 0.39
            self.refTexfieldUser.current.height = 50
            self.refTexfieldPassword.current.height = 50
            self.refBotonLogin.current.height = 50

        self.refContainerCuerpo.current.update()
    
    #Funcion para acutalizar la altura o tamaño de los elementos
    def update_height(self, height):
        width =self.page.width
        if height < 800:
            self.refTitulo.current.size = 22
            if width > 600:
                self.refTitulo.current.size = 27
            self.refContainerEncabezado.current.height = height * 0.07
            self.refContainerCuerpo.current.height = height * 0.35
            self.update_heightFooter(height)
        elif height < 1000:
            self.refTitulo.current.size = 24
            self.refContainerEncabezado.current.height = height * 0.07
            self.refContainerCuerpo.current.height = height * 0.37
            self.update_heightFooter(height)
        elif height < 1200:
            self.refTitulo.current.size = 30
            self.refContainerEncabezado.current.height = height * 0.08
            self.refContainerCuerpo.current.height = height * 0.38
            self.update_heightCuerpo(height)
            self.update_heightFooter(height)
        elif height < 1400:
            self.refContainerGoogle.current.height = height * 0.13
            self.refContainerEncabezado.current.height = height * 0.16
            self.update_heightFooter(height)
        
        self.update_elements()