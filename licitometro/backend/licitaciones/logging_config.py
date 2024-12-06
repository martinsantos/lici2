import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

def setup_logging(log_dir: str = None, log_level: int = logging.INFO):
    """
    Configurar logging centralizado para el proyecto de licitaciones
    
    Args:
        log_dir (str, optional): Directorio para guardar logs. 
                                 Si no se especifica, usa un directorio 'logs' en el directorio actual.
        log_level (int, optional): Nivel de logging. Por defecto INFO.
    
    Returns:
        logging.Logger: Logger raíz configurado
    """
    # Directorio de logs
    if log_dir is None:
        log_dir = os.path.join(os.path.dirname(__file__), 'logs')
    
    # Crear directorio de logs si no existe
    os.makedirs(log_dir, exist_ok=True)
    
    # Nombre de archivo de log con fecha
    log_filename = os.path.join(
        log_dir, 
        f'licitaciones_{datetime.now().strftime("%Y%m%d")}.log'
    )
    
    # Configurar logger raíz
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[]  # Limpiar handlers por defecto
    )
    
    # Crear handler de archivo rotativo
    file_handler = RotatingFileHandler(
        log_filename, 
        maxBytes=10*1024*1024,  # 10 MB
        backupCount=5  # Mantener 5 archivos de backup
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    
    # Crear handler de consola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(logging.Formatter(
        '%(name)s - %(levelname)s - %(message)s'
    ))
    
    # Obtener logger raíz
    root_logger = logging.getLogger()
    root_logger.handlers.clear()  # Limpiar handlers existentes
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    return root_logger

def get_logger(name: str = None, log_level: int = logging.INFO):
    """
    Obtener un logger con configuración predeterminada
    
    Args:
        name (str, optional): Nombre del logger. Si no se especifica, usa el nombre del módulo.
        log_level (int, optional): Nivel de logging. Por defecto INFO.
    
    Returns:
        logging.Logger: Logger configurado
    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    return logger

# Configuración de logging al importar el módulo
setup_logging()
