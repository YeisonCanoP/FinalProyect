import flet as ft

class ViewLogin:
    def __init__(self, page: ft.Page):
        self.page = page
        # Contenedor principal asignado luego
        self.cont_login = None
        # Registrar evento de resize
        self.page.on_resize = self.on_resize

    def on_resize(self, e: ft.WindowResizeEvent):
        # Obtener altura actual
        h = self.page.height
        # Definir máximo 80% de la ventana o 600px
        max_h = min(600, h * 0.8)
        if self.cont_login:
            self.cont_login.height = max_h
            self.page.update()

    def crear_fondo(self):
        return ft.Container(
            expand=True,
            content=ft.Image(src=self.imagen_fondo, expand=True, fit=ft.ImageFit.FILL),
        )

    def create_container(self):
        # Creamos el contenedor principal del login sin height fijo inicial
        # Se asignará y ajustará en on_resize
        self.cont_login = ft.Container(
            # height se asigna en on_resize
            alignment=ft.alignment.center,
            gradient=ft.LinearGradient(
                begin=ft.alignment.bottom_left,
                end=ft.alignment.top_right,
                colors=["#FF6B81", "#FF8CD1", "#8C7BFF", "#8A7FD9"],
            ),
            opacity=0.4,
            border_radius=25,
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    # Aquí pondrías los campos de login
                    ft.TextField(label="Usuario"),
                    ft.TextField(label="Contraseña", password=True),
                    ft.ElevatedButton("Entrar", on_click=self.on_login),
                ],
            ),
        )
        # Añadir espaciadores en una Column padre para centrar vertical
        column_padre = ft.Column(
            expand=True,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Container(expand=1),
                ft.Container(content=self.cont_login),
                ft.Container(expand=1),
            ],
        )
        return column_padre

    def create_login(self):
        fondo_contenido = ft.Stack(
            expand=True,
            controls=[
                self.crear_fondo(),
                ft.Container(
                    expand=True,
                    content=self.create_container(),
                ),
            ],
        )
        self.page.add(fondo_contenido)
        # Forzar primer ajuste
        # Llamamos on_resize manualmente para establecer altura inicial:
        class Dummy: pass
        dummy = Dummy()
        dummy.height = self.page.height
        self.on_resize(dummy)
        self.page.padding = 0
        self.page.expand = True
        self.page.update()
