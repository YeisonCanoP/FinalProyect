import flet as ft
import jwt

def main(page: ft.Page):
    page.title = "Vizora Auth"

    # 1. Obtener token desde URL (por ejemplo: /?token=eyJ...)
    token = page.query_params.get("token")
    user_email = None

    if token:
        try:
            # Opcional: validar firma con la clave pública de Cognito (más seguro)
            decoded = jwt.decode(token, options={"verify_signature": False})
            user_email = decoded.get("email")
        except Exception as e:
            print("Error decoding token:", e)

    if user_email:
        page.add(
            ft.Text(f"Bienvenido {user_email}"),
            ft.ElevatedButton("Cerrar sesión", on_click=lambda _: page.launch_url("http://localhost:8000/logout"))
        )
    else:
        page.add(
            ft.Text("No has iniciado sesión."),
            ft.ElevatedButton("Iniciar sesión con Google", on_click=lambda _: page.launch_url("http://localhost:8000/login"))
        )

ft.app(target=main, view=ft.WEB_BROWSER)
