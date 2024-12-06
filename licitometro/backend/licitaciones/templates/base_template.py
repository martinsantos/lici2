from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
from datetime import datetime
import logging
import re
import requests
from dateutil.parser import parse as dateutil_parse

logger = logging.getLogger(__name__)

class RequestManager:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def get(self, url, **kwargs):
        return self.session.get(url, **kwargs)

class ScrapingProgress:
    def __init__(self):
        self.total_records = 0
        self.saved_records = 0
        self.error_records = 0
        self.processed = 0
        self.current_status = ""
        self.errors = []

    def increment_total(self):
        self.total_records += 1

    def increment_saved(self):
        self.saved_records += 1

    def increment_error(self):
        self.error_records += 1

    def add_error(self, error):
        self.errors.append(error)

class BaseLicitacionTemplate(ABC):
    # Formatos de fecha comunes en Argentina
    DATE_FORMATS = [
        "%d/%m/%Y",  # 31/12/2023
        "%d-%m-%Y",  # 31-12-2023
        "%Y-%m-%d",  # 2023-12-31
        "%d/%m/%y",  # 31/12/23
        "%d-%m-%y",  # 31-12-23
        "%m/%d/%Y",  # 12/31/2023 (added for US format)
        "%m-%d-%Y",  # 12-31-2023
        "%d/%m/%Y %H:%M:%S",  # 31/12/2023 14:30:00
        "%d-%m-%Y %H:%M:%S",  # 31-12-2023 14:30:00
        "%Y/%m/%d",  # 2023/12/31
        "%Y-%m-%d %H:%M:%S",  # 2023-12-31 14:30:00
        "%Y/%m/%d %H:%M:%S",  # 2023/12/31 14:30:00
        "%d/%m/%y %H:%M %p",  # 31/12/23 02:30 PM
    ]

    def __init__(self, url: Optional[str] = None):
        self.url = url
        self.request_manager = RequestManager()
        self.progress = ScrapingProgress()
        # Common headers to avoid being blocked
        self.request_manager.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def extract_licitaciones(self) -> List[Dict]:
        """
        Extract licitaciones data from the source.
        Returns a list of dictionaries with standardized fields.
        """
        try:
            # Fetch page content
            soup = self.get_page_content(self.url)
            if not soup:
                logger.error(f"Failed to fetch page content from {self.url}")
                return []

            # Find the main container for licitaciones
            main_container = self._find_main_container(soup)
            if not main_container:
                logger.error(f"No main container found in {self.url}")
                return []

            # Extract individual licitaciones
            licitaciones = []
            licitacion_elements = self._find_licitacion_elements(main_container)
            
            if not licitacion_elements:
                logger.warning(f"No licitacion elements found in main container for {self.url}")
                return []

            logger.info(f"Found {len(licitacion_elements)} potential licitaciones in {self.url}")

            for element in licitacion_elements:
                try:
                    licitacion = self._extract_licitacion_details(element)
                    if licitacion:
                        licitaciones.append(licitacion)
                except Exception as e:
                    logger.warning(f"Error extracting individual licitacion: {str(e)}")

            logger.info(f"Successfully extracted {len(licitaciones)} valid licitaciones from {self.url}")
            return licitaciones

        except Exception as e:
            logger.error(f"Unexpected error in extract_licitaciones: {str(e)}")
            return []

    def _find_main_container(self, soup: BeautifulSoup) -> Optional[Any]:
        """
        Find the main container for licitaciones in the parsed HTML.
        Default implementation logs a warning and returns None.
        """
        logger.warning(f"No main container method implemented for {self.url}")
        return None

    def _find_licitacion_elements(self, main_container: Any) -> List[Any]:
        """
        Find individual licitacion elements within the main container.
        Default implementation logs a warning and returns an empty list.
        """
        logger.warning(f"No licitacion elements method implemented for {self.url}")
        return []

    def _extract_licitacion_details(self, element: Any) -> Optional[Dict]:
        """
        Extract details for a single licitacion from an element.
        Default implementation logs a warning and returns None.
        """
        logger.warning(f"No licitacion details extraction method implemented for {self.url}")
        return None

    def get_page_content(self, url: Optional[str] = None) -> Optional[BeautifulSoup]:
        """
        Fetch page content and return BeautifulSoup object
        """
        if not url:
            url = self.url

        if not url:
            logger.error("No URL provided for scraping")
            return None

        try:
            self.progress.current_status = f"Obteniendo página: {url}"
            response = self.request_manager.get(url, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            error_msg = f"Error fetching {url}: {str(e)}"
            logger.error(error_msg)
            self.progress.add_error(error_msg)
            return None

    def clean_text(self, text: str) -> str:
        """
        Clean and standardize text fields
        """
        if not text:
            return ""
        # Remove extra whitespace and normalize
        text = " ".join(text.strip().split())
        # Remove common prefixes
        text = re.sub(r'^(fecha:?\s*|publicado:?\s*|estado:?\s*|organismo:?\s*)', '', text.lower())
        return text.strip()

    def _adjust_two_digit_year(self, year_str: str) -> str:
        """
        Adjust two-digit years to four-digit years with intelligent inference.
        Assumes years less than 50 are in 2000s, 50-99 are in 1900s.
        """
        try:
            year = int(year_str)
            if year < 50:
                return str(2000 + year)
            elif year < 100:
                return str(1900 + year)
            return year_str
        except ValueError:
            return year_str

    def parse_date(self, date_str: Optional[str], format_str: Optional[str] = None) -> Optional[datetime]:
        """
        Enhanced date parsing with robust handling of problematic formats.
        """
        if not date_str:
            return None
        
        # Skip strings that are clearly not dates
        if not date_str or date_str.lower() in ['publicado', 'pendiente', 'en proceso', 'n/a']:
            return None

        # Clean and preprocess the date string
        date_str = self.clean_text(date_str)
        
        # Remove any time information
        date_str = date_str.split()[0]
        
        # Normalize separators and remove extra spaces
        date_str = re.sub(r'\s+', '', date_str.replace('/', '-'))
        
        # Skip single digit or empty strings
        if len(date_str) < 3:
            logger.warning(f"Skipping invalid date: {date_str}")
            return None

        # Try multiple parsing strategies
        parsing_strategies = [
            # Direct parsing attempts
            lambda x: datetime.strptime(x, "%d-%m-%Y"),
            lambda x: datetime.strptime(x, "%m-%d-%Y"),
            lambda x: datetime.strptime(x, "%Y-%m-%d"),
            
            # Flexible parsing with dateutil
            lambda x: dateutil_parse(x, fuzzy=True) if x else None
        ]

        for strategy in parsing_strategies:
            try:
                parsed_date = strategy(date_str)
                if parsed_date:
                    # Validate month and year
                    if parsed_date.month > 12 or parsed_date.year < 1900 or parsed_date.year > 2100:
                        logger.warning(f"Invalid date after parsing: {date_str}")
                        continue
                    return parsed_date
            except Exception as e:
                logger.debug(f"Date parsing failed for {date_str}: {str(e)}")
                continue

        # Additional fallback for specific problematic formats
        try:
            # Try swapping month and day
            parts = date_str.split('-')
            if len(parts) == 3:
                # Try swapping first two parts
                swapped_date_str = f"{parts[1]}-{parts[0]}-{parts[2]}"
                for strategy in parsing_strategies:
                    try:
                        parsed_date = strategy(swapped_date_str)
                        if parsed_date:
                            return parsed_date
                    except Exception:
                        continue
        except Exception:
            pass

        logger.warning(f"Could not parse date: {date_str}")
        return None

    def extract_date_from_text(self, text: str) -> Optional[str]:
        """
        Extract a date from a text string that may contain other information
        """
        # Patrones comunes de fecha en texto
        patterns = [
            r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',  # dd/mm/yyyy o dd-mm-yyyy
            r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})',    # yyyy/mm/dd o yyyy-mm-dd
            r'(\d{1,2}[-/]\d{1,2}[-/]\d{2})',    # dd/mm/yy o dd-mm-yy
        ]
        
        text = self.clean_text(text)
        
        # Intentar extraer la fecha usando los patrones
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
                
        return None

    def format_date(self, date_obj) -> Optional[str]:
        """Format a date object to string in ISO format"""
        if not date_obj:
            return None
        if isinstance(date_obj, str):
            return date_obj
        try:
            return date_obj.strftime("%Y-%m-%d")
        except Exception as e:
            error_msg = f"Error formatting date: {str(e)}"
            logger.error(error_msg)
            self.progress.add_error(error_msg)
            return None

    def validate_licitacion(self, licitacion: Dict) -> bool:
        """
        Enhanced validation with flexible requirements and intelligent defaults.
        """
        validation_errors = []
        
        # Título is still critical
        if not licitacion.get('titulo'):
            validation_errors.append("Título es obligatorio")
        
        # Relax identifier requirements
        if not any([
            licitacion.get('titulo'), 
            licitacion.get('numero_licitacion'), 
            licitacion.get('numero_expediente')
        ]):
            validation_errors.append("Necesita al menos un identificador")
        
        # More flexible field validation
        minimal_fields = ['organismo']
        missing_fields = [field for field in minimal_fields if not licitacion.get(field)]
        
        if missing_fields:
            validation_errors.append(f"Campos faltantes: {', '.join(missing_fields)}")
        
        # Intelligent date handling
        date_fields = ['fecha_publicacion', 'fecha_apertura']
        valid_date_found = False
        for date_field in date_fields:
            if date_value := licitacion.get(date_field):
                try:
                    parsed_date = self.parse_date(date_value)
                    if parsed_date:
                        valid_date_found = True
                        break
                except Exception as e:
                    validation_errors.append(f"Error parseando {date_field}: {str(e)}")
        
        # If no valid date found, use current date
        if not valid_date_found:
            licitacion['fecha_publicacion'] = datetime.now().strftime("%Y-%m-%d")
        
        # Validate estado, but make it optional
        if not licitacion.get('estado'):
            licitacion['estado'] = 'Pendiente'
        
        if validation_errors:
            error_msg = f"Licitación con advertencias: {' | '.join(validation_errors)}"
            logger.warning(error_msg)
            self.progress.add_error(error_msg)
        
        return True  # Always return True, but log warnings

    def standardize_licitacion(self, licitacion: Dict) -> Dict:
        """
        Enhanced standardization with more intelligent defaults and recovery.
        """
        self.progress.current_status = f"Estandarizando licitación: {licitacion.get('titulo', 'Sin título')}"
        
        # Campos por defecto con más contexto
        default_licitacion = {
            'estado': 'Pendiente',
            'organismo': 'Sin organismo definido',
            'descripcion': 'Sin descripción',
            'categoria': 'General',
            'moneda': 'ARS',  # Moneda por defecto
        }
        
        # Combinar con valores por defecto
        for key, default_value in default_licitacion.items():
            if not licitacion.get(key):
                licitacion[key] = default_value
        
        # Generar ID único con más robustez
        if 'id' not in licitacion:
            base_id = (
                licitacion.get('numero_licitacion') or 
                licitacion.get('numero_expediente') or 
                f"{licitacion['organismo']}-{licitacion['titulo']}"
            )
            licitacion['id'] = str(uuid.uuid5(uuid.NAMESPACE_DNS, base_id))
        
        # Limpiar campos de texto
        text_fields = ['titulo', 'descripcion', 'organismo', 'estado', 'categoria']
        for field in text_fields:
            if field in licitacion:
                licitacion[field] = self.clean_text(licitacion[field])
        
        # Parsear y formatear fechas con más flexibilidad
        date_fields = ['fecha_publicacion', 'fecha_apertura']
        for field in date_fields:
            if field in licitacion:
                parsed_date = self.parse_date(licitacion[field])
                if not parsed_date and field == 'fecha_publicacion':
                    # Fallback to fecha_apertura if publication date is missing
                    parsed_date = self.parse_date(licitacion.get('fecha_apertura', ''))
                
                licitacion[field] = self.format_date(parsed_date) or datetime.now().strftime("%Y-%m-%d")
        
        # Campos numéricos con valor por defecto
        numeric_fields = ['monto', 'presupuesto']
        for field in numeric_fields:
            if field in licitacion:
                try:
                    licitacion[field] = float(str(licitacion[field]).replace(',', '.'))
                except (ValueError, TypeError):
                    licitacion[field] = 0.0
        
        # Campos de lista con valor por defecto
        list_fields = ['requisitos', 'documentos', 'extractos']
        for field in list_fields:
            if field not in licitacion or not licitacion[field]:
                licitacion[field] = []
        
        self.progress.processed += 1
        return licitacion
