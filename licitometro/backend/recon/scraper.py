import scrapy
from scrapy.crawler import CrawlerProcess
from typing import Dict, Any, Optional, List
import json
import logging
import hashlib
from datetime import datetime
import re
from urllib.parse import urljoin

class AdvancedFlexibleSpider(scrapy.Spider):
    """
    Spider avanzado y configurable para scraping de licitaciones
    """
    name = 'advanced_flexible_spider'

    def __init__(self, template: Dict[str, Any], *args, **kwargs):
        """
        Inicializa el spider con una plantilla de configuración avanzada
        
        :param template: Diccionario de configuración de la plantilla
        """
        super().__init__(*args, **kwargs)
        self.template = template
        self.start_urls = [template.get('source_url')]
        self.field_mapping = template.get('field_mapping', {})
        self.transformation_rules = template.get('transformation_rules', {})
        self.pagination_config = template.get('pagination', {})
        self.max_pages = template.get('max_pages', 5)
        self.current_page = 1

    def parse(self, response):
        """
        Parsea la respuesta según la configuración de la plantilla
        """
        # Selector base (por defecto usa CSS, permite XPath)
        selector_type = self.template.get('selector_type', 'css')
        item_selector = self.template.get('item_selector', 'div.item')

        # Extrae elementos
        items = response.css(item_selector) if selector_type == 'css' else response.xpath(item_selector)

        for item in items:
            scraped_item = self._extract_item_data(item)
            
            # Generar hash único para identificación
            scraped_item['unique_hash'] = self._generate_item_hash(scraped_item)
            
            yield scraped_item

        # Manejo de paginación
        if self._should_continue_pagination(response):
            next_page = self._get_next_page_url(response)
            if next_page:
                self.current_page += 1
                yield response.follow(next_page, self.parse)

    def _extract_item_data(self, item):
        """
        Extrae datos de un elemento individual
        """
        scraped_item = {
            'source_url': self.start_urls[0],
            'scraped_at': datetime.utcnow().isoformat()
        }

        for target_field, field_config in self.field_mapping.items():
            try:
                selector = field_config.get('selector')
                extraction_method = field_config.get('method', 'get_text')
                
                if extraction_method == 'get_text':
                    value = item.css(selector).get()
                elif extraction_method == 'get_attr':
                    attr = field_config.get('attr', 'href')
                    value = item.css(f'{selector}::attr({attr})').get()
                elif extraction_method == 'get_all_text':
                    value = ' '.join(item.css(selector).getall())
                else:
                    value = None

                # Aplicar transformaciones
                if 'transformation_rules' in field_config:
                    value = self._apply_transformation(value, field_config['transformation_rules'])

                scraped_item[target_field] = value
            except Exception as e:
                logging.error(f"Error extrayendo campo {target_field}: {e}")

        return scraped_item

    def _apply_transformation(self, value: Any, transform_config: Dict[str, Any]) -> Any:
        """
        Aplica transformaciones avanzadas a los valores extraídos
        """
        if not value:
            return value

        try:
            transform_type = transform_config.get('type')

            if transform_type == 'strip':
                return value.strip()
            elif transform_type == 'regex':
                pattern = transform_config.get('pattern')
                match = re.search(pattern, value)
                return match.group(1) if match else value
            elif transform_type == 'date_parse':
                from dateutil.parser import parse
                return parse(value).isoformat()
            elif transform_type == 'clean_whitespace':
                return re.sub(r'\s+', ' ', value).strip()
            elif transform_type == 'absolute_url':
                return urljoin(self.start_urls[0], value)
            
            return value
        except Exception as e:
            logging.error(f"Error en transformación: {e}")
            return value

    def _generate_item_hash(self, item: Dict[str, Any]) -> str:
        """
        Genera un hash único para un elemento para evitar duplicados
        """
        # Usa campos clave para generar hash
        hash_fields = ['titulo', 'fecha', 'url']
        hash_string = '|'.join(str(item.get(field, '')) for field in hash_fields)
        return hashlib.md5(hash_string.encode()).hexdigest()

    def _should_continue_pagination(self, response) -> bool:
        """
        Determina si se debe continuar con la paginación
        """
        return (
            self.current_page < self.max_pages and 
            self.pagination_config.get('enabled', False)
        )

    def _get_next_page_url(self, response):
        """
        Obtiene la URL de la siguiente página según configuración
        """
        next_page_selector = self.pagination_config.get('selector')
        
        if not next_page_selector:
            return None

        next_page = response.css(next_page_selector).get()
        return next_page

class ScraperManager:
    """
    Gestor avanzado para ejecución de scrapers
    """
    @staticmethod
    def run_scraper(template: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Ejecuta un scraper con una plantilla específica
        
        :param template: Configuración de la plantilla de scraping
        :return: Lista de elementos extraídos
        """
        results = []
        
        def collect_item(item):
            results.append(item)

        process = CrawlerProcess(settings={
            'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'ROBOTSTXT_OBEY': True,
            'DOWNLOAD_DELAY': 1,  # Respetar política de scraping
            'CONCURRENT_REQUESTS': 1  # Solicitudes concurrentes
        })

        spider = type('ConfigurableSpider', (AdvancedFlexibleSpider,), {})
        process.crawl(spider, template=template, callback=collect_item)
        process.start()

        return results

# Ejemplo de uso
if __name__ == '__main__':
    template_example = {
        'source_url': 'https://ejemplo.com/licitaciones',
        'item_selector': 'div.licitacion',
        'field_mapping': {
            'titulo': {'selector': 'h2.titulo', 'method': 'get_text'},
            'fecha': {
                'selector': 'span.fecha', 
                'method': 'get_text', 
                'transformation_rules': {'type': 'date_parse'}
            },
            'url': {
                'selector': 'a.detalle', 
                'method': 'get_attr', 
                'attr': 'href',
                'transformation_rules': {'type': 'absolute_url'}
            }
        },
        'pagination': {
            'enabled': True,
            'selector': 'a.next-page'
        },
        'max_pages': 3
    }

    resultados = ScraperManager.run_scraper(template_example)
    print(json.dumps(resultados, indent=2, ensure_ascii=False))
