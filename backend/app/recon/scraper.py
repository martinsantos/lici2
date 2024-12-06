import scrapy
from scrapy.crawler import CrawlerProcess
from datetime import datetime
from typing import Dict, Any, Optional
import hashlib
import json

class LicitacionScraper(scrapy.Spider):
    name = 'licitacion_scraper'
    
    def __init__(self, plantilla: Dict[str, Any], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plantilla = plantilla
        self.start_urls = [plantilla['configuracion_fuente']['url_inicial']]
        self.reglas = plantilla['reglas']
        self.mapeo = plantilla['mapeo']
    
    def parse(self, response):
        # Aplicar reglas de extracción según la plantilla
        for selector in self.reglas['selectores_lista']:
            for item in response.css(selector):
                licitacion = {}
                
                # Extraer campos según el mapeo
                for campo_destino, config in self.mapeo.items():
                    valor = None
                    if config['tipo'] == 'css':
                        valor = item.css(config['selector']).get()
                    elif config['tipo'] == 'xpath':
                        valor = item.xpath(config['selector']).get()
                    
                    # Aplicar transformaciones si existen
                    if valor and 'transformaciones' in config:
                        valor = self.aplicar_transformaciones(valor, config['transformaciones'])
                    
                    licitacion[campo_destino] = valor
                
                # Agregar metadatos
                licitacion['fuente_datos'] = self.plantilla['fuente']
                licitacion['ultima_actualizacion'] = datetime.now().isoformat()
                licitacion['url_origen'] = response.url
                licitacion['hash_contenido'] = self.generar_hash(licitacion)
                
                yield licitacion
        
        # Seguir enlaces según las reglas de paginación
        if 'selector_siguiente' in self.reglas:
            siguiente = response.css(self.reglas['selector_siguiente']).get()
            if siguiente:
                yield response.follow(siguiente, self.parse)
    
    def aplicar_transformaciones(self, valor: str, transformaciones: list) -> Any:
        for trans in transformaciones:
            if trans['tipo'] == 'fecha':
                valor = datetime.strptime(valor, trans['formato'])
            elif trans['tipo'] == 'numero':
                valor = float(valor.replace(',', '').replace('$', ''))
            elif trans['tipo'] == 'texto':
                valor = valor.strip()
        return valor
    
    def generar_hash(self, data: dict) -> str:
        # Generar hash único del contenido
        contenido = json.dumps(data, sort_keys=True)
        return hashlib.sha256(contenido.encode()).hexdigest()

def ejecutar_scraper(plantilla: Dict[str, Any]) -> None:
    process = CrawlerProcess({
        'USER_AGENT': 'Licitometro/1.0 (+http://licitometro.com)',
        'ROBOTSTXT_OBEY': True,
        'CONCURRENT_REQUESTS': 16,
        'DOWNLOAD_DELAY': 1,
    })
    
    process.crawl(LicitacionScraper, plantilla=plantilla)
    process.start()
