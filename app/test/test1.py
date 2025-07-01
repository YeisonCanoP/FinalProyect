from PIL import Image

# Abrir imagen original
imagen = Image.open("app/assets/fondo-melocoton-degradado-con-tonos-rosados.jpg")

# Redimensionar si es muy grande (opcional)
imagen = imagen.resize((1920,1080))  # o el tamaño que necesites

# Guardar como WebP con compresión alta
imagen.save("app/assets/fondo_login.webp", format="webp", quality=90, method=6)