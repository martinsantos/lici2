import os
import json
import yaml
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict, field

from ..logging_config import get_logger

@dataclass
class ScraperConfig:
    """
    Configuración para scrapers de licitaciones
    """
    nombre: str
    url_base: str
    urls_secundarias: List[str] = field(default_factory=list)
    
    # Configuraciones de scraping
    max_paginas: int = 5
    intervalo_solicitudes: float = 1.0  # Segundos entre solicitudes
    usar_proxy: bool = True
    
    # Filtros de licitaciones
    filtros: Dict[str, Any] = field(default_factory=dict)
    
    # Configuraciones de logging
    log_level: str = 'INFO'
    
    # Configuraciones de persistencia
    guardar_en_bd: bool = True
    db_path: Optional[str] = None

class ScraperConfigManager:
    """
    Gestiona configuraciones de scrapers
    """
    def __init__(self, config_dir: str = None):
        """
        Inicializar gestor de configuración
        
        Args:
            config_dir (str, optional): Directorio de configuraciones. 
                                        Por defecto usa un directorio 'config' en el proyecto.
        """
        self.logger = get_logger(self.__class__.__name__)
        
        if config_dir is None:
            config_dir = os.path.join(
                os.path.dirname(__file__), 
                '..'
            )
        
        self.config_dir = config_dir
        self.configs_dir = os.path.join(config_dir, 'configs')
        
        # Crear directorio de configuraciones si no existe
        os.makedirs(self.configs_dir, exist_ok=True)

    def crear_configuracion(
        self, 
        nombre: str, 
        url_base: str, 
        **kwargs
    ) -> ScraperConfig:
        """
        Crear una nueva configuración de scraper
        
        Args:
            nombre (str): Nombre del scraper
            url_base (str): URL base del scraper
            **kwargs: Argumentos adicionales de configuración
        
        Returns:
            ScraperConfig: Configuración creada
        """
        config = ScraperConfig(
            nombre=nombre,
            url_base=url_base,
            **kwargs
        )
        
        self.guardar_configuracion(config)
        return config

    def guardar_configuracion(self, config: ScraperConfig):
        """
        Guardar configuración en archivo YAML
        
        Args:
            config (ScraperConfig): Configuración a guardar
        """
        try:
            # Convertir configuración a diccionario
            config_dict = asdict(config)
            
            # Nombre de archivo
            filename = f"{config.nombre.lower().replace(' ', '_')}_config.yaml"
            filepath = os.path.join(self.configs_dir, filename)
            
            # Guardar en YAML
            with open(filepath, 'w', encoding='utf-8') as f:
                yaml.safe_dump(config_dict, f, default_flow_style=False, allow_unicode=True)
            
            self.logger.info(f"Configuración guardada en {filepath}")
        
        except Exception as e:
            self.logger.error(f"Error guardando configuración: {e}")

    def cargar_configuracion(self, nombre: str) -> Optional[ScraperConfig]:
        """
        Cargar configuración desde archivo YAML
        
        Args:
            nombre (str): Nombre del scraper
        
        Returns:
            Optional[ScraperConfig]: Configuración cargada o None si no existe
        """
        try:
            # Nombre de archivo
            filename = f"{nombre.lower().replace(' ', '_')}_config.yaml"
            filepath = os.path.join(self.configs_dir, filename)
            
            # Verificar existencia
            if not os.path.exists(filepath):
                self.logger.warning(f"No se encontró configuración para {nombre}")
                return None
            
            # Cargar desde YAML
            with open(filepath, 'r', encoding='utf-8') as f:
                config_dict = yaml.safe_load(f)
            
            # Convertir a ScraperConfig
            return ScraperConfig(**config_dict)
        
        except Exception as e:
            self.logger.error(f"Error cargando configuración: {e}")
            return None

    def listar_configuraciones(self) -> List[str]:
        """
        Listar nombres de configuraciones disponibles
        
        Returns:
            List[str]: Lista de nombres de configuraciones
        """
        try:
            # Obtener archivos YAML en el directorio
            configs = [
                f.replace('_config.yaml', '') 
                for f in os.listdir(self.configs_dir) 
                if f.endswith('_config.yaml')
            ]
            return configs
        
        except Exception as e:
            self.logger.error(f"Error listando configuraciones: {e}")
            return []

    def actualizar_configuracion(
        self, 
        nombre: str, 
        **kwargs
    ) -> Optional[ScraperConfig]:
        """
        Actualizar una configuración existente
        
        Args:
            nombre (str): Nombre del scraper
            **kwargs: Campos a actualizar
        
        Returns:
            Optional[ScraperConfig]: Configuración actualizada o None
        """
        config = self.cargar_configuracion(nombre)
        
        if config is None:
            return None
        
        # Actualizar campos
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        # Guardar configuración actualizada
        self.guardar_configuracion(config)
        
        return config

    def eliminar_configuracion(self, nombre: str) -> bool:
        """
        Eliminar una configuración
        
        Args:
            nombre (str): Nombre del scraper
        
        Returns:
            bool: True si se eliminó, False en caso de error
        """
        try:
            # Nombre de archivo
            filename = f"{nombre.lower().replace(' ', '_')}_config.yaml"
            filepath = os.path.join(self.configs_dir, filename)
            
            # Eliminar archivo
            if os.path.exists(filepath):
                os.remove(filepath)
                self.logger.info(f"Configuración {nombre} eliminada")
                return True
            
            self.logger.warning(f"No se encontró configuración para {nombre}")
            return False
        
        except Exception as e:
            self.logger.error(f"Error eliminando configuración: {e}")
            return False

# Función de utilidad para crear una instancia
def obtener_config_manager(config_dir: str = None) -> ScraperConfigManager:
    """
    Obtener una instancia de ScraperConfigManager
    
    Args:
        config_dir (str, optional): Directorio de configuraciones
    
    Returns:
        ScraperConfigManager: Instancia de gestor de configuración
    """
    return ScraperConfigManager(config_dir)
