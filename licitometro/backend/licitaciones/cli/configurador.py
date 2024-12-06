import os
import json
import click
from typing import Dict, Any

from ..notifications.notificador import obtener_notificador
from ..config.scraper_config import obtener_config_manager

class Configurador:
    def __init__(self):
        """
        Inicializar configurador de aplicación
        """
        self.notificador = obtener_notificador()
        self.config_manager = obtener_config_manager()

    def _cargar_configuracion(self, tipo: str) -> Dict[str, Any]:
        """
        Cargar configuración según el tipo
        
        Args:
            tipo (str): Tipo de configuración ('notificaciones' o 'scrapers')
        
        Returns:
            Dict[str, Any]: Configuración actual
        """
        if tipo == 'notificaciones':
            return self.notificador.config
        elif tipo == 'scrapers':
            return self.config_manager.listar_configuraciones()
        else:
            raise ValueError(f"Tipo de configuración no soportado: {tipo}")

    def _guardar_configuracion(self, tipo: str, config: Dict[str, Any]):
        """
        Guardar configuración según el tipo
        
        Args:
            tipo (str): Tipo de configuración ('notificaciones' o 'scrapers')
            config (Dict[str, Any]): Configuración a guardar
        """
        if tipo == 'notificaciones':
            self.notificador.guardar_configuracion(config)
        elif tipo == 'scrapers':
            for nombre, conf in config.items():
                self.config_manager.guardar_configuracion(nombre, conf)
        else:
            raise ValueError(f"Tipo de configuración no soportado: {tipo}")

@click.group()
def cli():
    """
    CLI de configuración para Licitometro
    """
    pass

@cli.command()
@click.argument('tipo', type=click.Choice(['notificaciones', 'scrapers']))
@click.option('--mostrar', is_flag=True, help='Mostrar configuración actual')
@click.option('--editar', is_flag=True, help='Editar configuración')
def configurar(tipo, mostrar, editar):
    """
    Gestionar configuraciones de la aplicación
    """
    configurador = Configurador()

    try:
        config_actual = configurador._cargar_configuracion(tipo)

        if mostrar:
            click.echo(f"Configuración actual de {tipo}:")
            click.echo(json.dumps(config_actual, indent=2))
            return

        if editar:
            config_editada = _editar_configuracion(config_actual)
            configurador._guardar_configuracion(tipo, config_editada)
            click.echo(f"Configuración de {tipo} actualizada exitosamente.")

    except Exception as e:
        click.echo(f"Error: {e}")

def _editar_configuracion(config_actual: Dict[str, Any]) -> Dict[str, Any]:
    """
    Editar configuración interactivamente
    
    Args:
        config_actual (Dict[str, Any]): Configuración actual
    
    Returns:
        Dict[str, Any]: Configuración editada
    """
    config_editada = config_actual.copy()

    def editar_seccion(seccion: Dict[str, Any], nombre_seccion: str) -> Dict[str, Any]:
        """
        Editar una sección de configuración
        """
        click.echo(f"\nEditando {nombre_seccion}:")
        for clave, valor in seccion.items():
            if isinstance(valor, (str, int, float, bool)):
                nuevo_valor = click.prompt(
                    f"  {clave} (actual: {valor})", 
                    default=valor, 
                    show_default=True
                )
                
                # Conversión de tipo
                if isinstance(valor, bool):
                    nuevo_valor = click.confirm(f"  {clave}", default=valor)
                elif isinstance(valor, int):
                    nuevo_valor = int(nuevo_valor)
                elif isinstance(valor, float):
                    nuevo_valor = float(nuevo_valor)
                
                seccion[clave] = nuevo_valor
            elif isinstance(valor, list):
                click.echo(f"  {clave} (lista actual: {valor})")
                accion = click.prompt(
                    "  Seleccione acción", 
                    type=click.Choice(['añadir', 'eliminar', 'reemplazar', 'mantener'])
                )
                
                if accion == 'añadir':
                    nuevo_item = click.prompt("  Nuevo elemento")
                    seccion[clave].append(nuevo_item)
                elif accion == 'eliminar':
                    item_eliminar = click.prompt("  Elemento a eliminar")
                    if item_eliminar in seccion[clave]:
                        seccion[clave].remove(item_eliminar)
                elif accion == 'reemplazar':
                    seccion[clave] = click.prompt(
                        "  Nueva lista (separada por comas)", 
                        value_proc=lambda x: [item.strip() for item in x.split(',')]
                    )
        
        return seccion

    # Editar secciones según tipo de configuración
    if 'email' in config_editada:  # Configuración de notificaciones
        for seccion in ['email', 'telegram', 'webhook', 'filtros']:
            config_editada[seccion] = editar_seccion(config_editada[seccion], seccion)
    else:  # Configuración de scrapers
        for nombre_config, config in config_editada.items():
            click.echo(f"\nEditando configuración: {nombre_config}")
            config_editada[nombre_config] = editar_seccion(config, nombre_config)

    return config_editada

def main():
    cli()

if __name__ == "__main__":
    main()
