import logging
from logging.handlers import RotatingFileHandler
import os 
import sys
sys.path.append("c:/Users/yeiso/OneDrive/Escritorio/Proyecto/final_proyect")
from app.utils.singleton import SingletonMeta

#Clase para manejar la creacion de logs y almacenarlos en un archivo de la aplicacion
class Logger(metaclass=SingletonMeta):
    #Constructor
    def __init__(self,log_file = "logs/app.log",level = logging.DEBUG):
        #Primero se asegura que la carpeta si exista
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

        #Se crea el logger
        self.logger = logging.getLogger(log_file)
        self.logger.setLevel(level)


        # Definir el formatter fuera del bloque condicional
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        # Evitar agregar handlers duplicados
        if not self.logger.hasHandlers():
            #Handler para archivo con rotacion (Sera solo para errores y critical )
            file_handler = RotatingFileHandler(log_file, maxBytes=5*1024*10, backupCount=3)
            file_handler.setFormatter(formatter)
            file_handler.setLevel(logging.ERROR)

            #Handler para consola (info y debug)
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            console_handler.setLevel(logging.INFO)

            #Agregar handlers al logger
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

    #Funcion para devolver el logger
    def get_logger(self):
        return self.logger