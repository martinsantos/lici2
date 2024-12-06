from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime
import re
from dataclasses import dataclass
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

@dataclass
class ScrapingProgress:
    """Class to track scraping progress"""
    total_found: int = 0
    processed: int = 0
    saved: int = 0
    errors: int = 0
    skipped: int = 0
    current_page: int = 1
    total_pages: Optional[int] = None
    current_status: str = "Iniciando"
    error_details: List[str] = None

    def __post_init__(self):
        self.error_details = []

    def add_error(self, error: str):
        """Add error message to tracking"""
        self.errors += 1
        self.error_details.append(error)

    def to_dict(self) -> dict:
        """Convert progress to dictionary"""
        return {
            "total_found": self.total_found,
            "processed": self.processed,
            "saved": self.saved,
            "errors": self.errors,
            "skipped": self.skipped,
            "current_page": self.current_page,
            "total_pages": self.total_pages,
            "current_status": self.current_status,
            "error_details": self.error_details[-5:] if self.error_details else []  # Last 5 errors
        }

class BaseScraper(ABC):
    def __init__(self, url: str):
        self.url = url
        self.session = requests.Session()
        self.progress = ScrapingProgress()
        # Add headers to mimic a browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    @abstractmethod
    def extract_licitaciones(self) -> List[Dict[str, Any]]:
        """Extract licitaciones from the source"""
        pass

    def get_page_content(self, url: str = None) -> BeautifulSoup:
        """Get page content and return BeautifulSoup object"""
        try:
            self.progress.current_status = f"Obteniendo página {self.progress.current_page}"
            response = self.session.get(url or self.url, verify=False, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            error_msg = f"Error obteniendo contenido de {url or self.url}: {str(e)}"
            self.progress.add_error(error_msg)
            logger.error(error_msg)
            raise

    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        return re.sub(r'\s+', ' ', text.strip())

    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string in multiple formats"""
        if not date_str:
            return None
            
        date_formats = [
            '%Y-%m-%d',
            '%d/%m/%Y',
            '%Y-%m-%d %H:%M:%S',
            '%d-%m-%Y',
            '%d.%m.%Y',
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        return None

    def extract_money(self, text: str) -> Optional[float]:
        """Extract monetary value from text"""
        if not text:
            return None
        try:
            # Remove currency symbols and convert to float
            amount = re.sub(r'[^\d.,]', '', text)
            # Handle different decimal separators
            if ',' in amount and '.' in amount:
                amount = amount.replace('.', '')  # Remove thousands separator
                amount = amount.replace(',', '.')  # Convert decimal separator
            elif ',' in amount:
                amount = amount.replace(',', '.')
            return float(amount)
        except:
            return None

    def normalize_url(self, url: str) -> str:
        """Normalize relative URLs to absolute URLs"""
        if not url:
            return ""
        return urljoin(self.url, url)

class ComprarMendozaScraper(BaseScraper):
    def extract_licitaciones(self) -> List[Dict[str, Any]]:
        """Extract licitaciones from Comprar Mendoza"""
        licitaciones = []
        
        try:
            soup = self.get_page_content()
            
            # Find the table containing licitaciones
            table = soup.find('table', {'id': 'dgLicitaciones'})
            if not table:
                self.progress.add_error("No se encontró la tabla de licitaciones")
                return []

            rows = table.find_all('tr')[1:]  # Skip header row
            self.progress.total_found = len(rows)
            self.progress.current_status = f"Encontradas {len(rows)} licitaciones para procesar"
            
            for row in rows:
                try:
                    self.progress.processed += 1
                    cols = row.find_all('td')
                    if len(cols) < 6:
                        continue

                    # Extract data with detailed logging
                    numero = self.clean_text(cols[0].text)
                    titulo = self.clean_text(cols[1].text)
                    organismo = self.clean_text(cols[2].text)
                    fecha_pub = self.parse_date(self.clean_text(cols[3].text))
                    fecha_ap = self.parse_date(self.clean_text(cols[4].text))
                    estado = self.clean_text(cols[5].text)
                    
                    # Get detail URL if available
                    url_detalle = None
                    if link := cols[0].find('a'):
                        url_detalle = self.normalize_url(link.get('href', ''))

                    licitacion = {
                        'numero_licitacion': numero,
                        'titulo': titulo,
                        'organismo': organismo,
                        'fecha_publicacion': fecha_pub,
                        'fecha_apertura': fecha_ap,
                        'estado': estado,
                        'url_detalle': url_detalle
                    }
                    
                    if all([titulo, organismo, estado]):
                        licitaciones.append(licitacion)
                        self.progress.saved += 1
                    else:
                        self.progress.add_error(f"Licitación {numero} incompleta")
                        
                except Exception as e:
                    self.progress.add_error(f"Error procesando fila: {str(e)}")
                    continue

            self.progress.current_status = "Completado"
            return licitaciones
            
        except Exception as e:
            self.progress.add_error(f"Error general: {str(e)}")
            return []

class ComprasAppsMendozaScraper(BaseScraper):
    def extract_licitaciones(self) -> List[Dict[str, Any]]:
        """Extract licitaciones from Compras Apps Mendoza"""
        licitaciones = []
        
        try:
            soup = self.get_page_content()
            
            # Find all licitacion cards
            cards = soup.find_all('div', class_='card')
            self.progress.total_found = len(cards)
            self.progress.current_status = f"Encontradas {len(cards)} licitaciones para procesar"
            
            for card in cards:
                try:
                    self.progress.processed += 1
                    
                    # Extract data
                    header = card.find('div', class_='card-header')
                    body = card.find('div', class_='card-body')
                    
                    if not header or not body:
                        self.progress.add_error("Card incompleta")
                        continue
                    
                    titulo = self.clean_text(body.find('h5', class_='card-title').text) if body.find('h5', class_='card-title') else None
                    fecha = None
                    fecha_elem = body.find('p', class_='text-muted')
                    if fecha_elem:
                        fecha = self.parse_date(self.clean_text(fecha_elem.text))
                    
                    estado = "Publicada"
                    estado_elem = header.find('span', class_='badge')
                    if estado_elem:
                        estado = self.clean_text(estado_elem.text)
                    
                    url_detalle = None
                    if link := card.find('a'):
                        url_detalle = self.normalize_url(link.get('href', ''))
                    
                    licitacion = {
                        'titulo': titulo,
                        'descripcion': self.clean_text(body.get_text()),
                        'fecha_publicacion': fecha,
                        'estado': estado,
                        'organismo': 'Gobierno de Mendoza',
                        'url_detalle': url_detalle
                    }
                    
                    if titulo:  # Título es el único campo requerido para este scraper
                        licitaciones.append(licitacion)
                        self.progress.saved += 1
                    else:
                        self.progress.add_error("Licitación sin título")
                        
                except Exception as e:
                    self.progress.add_error(f"Error procesando card: {str(e)}")
                    continue
            
            self.progress.current_status = "Completado"
            return licitaciones
            
        except Exception as e:
            self.progress.add_error(f"Error general: {str(e)}")
            return []

class ComprarArgentinaScraper(BaseScraper):
    def extract_licitaciones(self) -> List[Dict[str, Any]]:
        """Extract licitaciones from Comprar Argentina"""
        licitaciones = []
        
        try:
            soup = self.get_page_content()
            
            # Find the table containing licitaciones
            table = soup.find('table', {'id': 'ctl00_CPH1_dgResultado'})
            if not table:
                self.progress.add_error("No se encontró la tabla de licitaciones")
                return []

            rows = table.find_all('tr')[1:]  # Skip header row
            self.progress.total_found = len(rows)
            self.progress.current_status = f"Encontradas {len(rows)} licitaciones para procesar"
            
            for row in rows:
                try:
                    self.progress.processed += 1
                    cols = row.find_all('td')
                    if len(cols) < 7:
                        continue

                    # Extract data with detailed logging
                    numero = self.clean_text(cols[0].text)
                    titulo = self.clean_text(cols[1].text)
                    organismo = self.clean_text(cols[2].text)
                    fecha_pub = self.parse_date(self.clean_text(cols[3].text))
                    fecha_ap = self.parse_date(self.clean_text(cols[4].text))
                    monto = self.extract_money(cols[5].text)
                    estado = self.clean_text(cols[6].text)
                    
                    # Get detail URL if available
                    url_detalle = None
                    if link := cols[0].find('a'):
                        url_detalle = self.normalize_url(link.get('href', ''))

                    licitacion = {
                        'numero_licitacion': numero,
                        'titulo': titulo,
                        'organismo': organismo,
                        'fecha_publicacion': fecha_pub,
                        'fecha_apertura': fecha_ap,
                        'monto': monto,
                        'estado': estado,
                        'url_detalle': url_detalle
                    }
                    
                    if all([titulo, organismo, estado]):
                        licitaciones.append(licitacion)
                        self.progress.saved += 1
                    else:
                        self.progress.add_error(f"Licitación {numero} incompleta")
                        
                except Exception as e:
                    self.progress.add_error(f"Error procesando fila: {str(e)}")
                    continue

            self.progress.current_status = "Completado"
            return licitaciones
            
        except Exception as e:
            self.progress.add_error(f"Error general: {str(e)}")
            return []
