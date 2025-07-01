import sys
sys.path.append('c:/Users/yeiso/OneDrive/Escritorio/Proyecto/final_proyect')

# Metaclase para implementar el patrón Singleton.
class SingletonMeta(type):

    """
    Meta clase para implementar el patrón Singleton.
    Garantiza que solo exista una instancia de la clase en toda la aplicación.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            # Si no existe una instancia, crea una y guárdala.
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

    def reset_instance(cls):
        
        """
        Reinicia la instancia del Singleton, si existe.
        """

        if cls in cls._instances:
            print(f"Reiniciando instancia de {cls.__name__}")
            cls._instances.pop(cls, None)


    @classmethod
    def reset_all_instances(cls):
        """
        Reinicia todas las instancias del Singleton.
        """
        for cls_name, instance in cls._instances.items():
            if hasattr(instance, "cerrar_conexion"):
                instance.cerrar_conexion()  # Llamar al método para cerrar conexión si existe
        cls._instances.clear()  # Elimina todas las instancias del Singleton