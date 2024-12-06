import logging
from typing import Dict, List, Any
from datetime import datetime
import uuid
import re

class ScrapingDiagnostics:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.DEBUG)

    def validate_licitacion_comprehensive(self, licitacion: Dict) -> Dict[str, Any]:
        """
        Realizar una validación exhaustiva de la licitación con diagnóstico detallado
        """
        diagnostics = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'suggestions': []
        }

        # Validaciones de campos críticos
        critical_fields = ['titulo', 'organismo', 'estado', 'fecha_publicacion']
        for field in critical_fields:
            if not licitacion.get(field):
                diagnostics['errors'].append(f"Campo crítico faltante: {field}")
                diagnostics['is_valid'] = False

        # Validación de fechas
        date_fields = ['fecha_publicacion', 'fecha_apertura']
        for field in date_fields:
            if value := licitacion.get(field):
                try:
                    datetime.fromisoformat(str(value).replace('Z', '+00:00'))
                except ValueError:
                    diagnostics['errors'].append(f"Formato de fecha inválido en {field}: {value}")
                    diagnostics['is_valid'] = False

        # Validación de campos numéricos
        numeric_fields = ['monto', 'presupuesto']
        for field in numeric_fields:
            if value := licitacion.get(field):
                try:
                    float(str(value).replace(',', '.'))
                except (ValueError, TypeError):
                    diagnostics['warnings'].append(f"Campo numérico no válido en {field}: {value}")

        # Generación de ID único si no existe
        if not licitacion.get('id'):
            base_id = (
                licitacion.get('numero_licitacion') or 
                licitacion.get('numero_expediente') or 
                f"{licitacion.get('organismo', 'SIN_ORGANISMO')}-{licitacion.get('titulo', 'SIN_TITULO')}"
            )
            licitacion['id'] = str(uuid.uuid5(uuid.NAMESPACE_DNS, base_id))
            diagnostics['suggestions'].append(f"ID generado automáticamente: {licitacion['id']}")

        # Limpieza de texto
        text_fields = ['titulo', 'descripcion', 'organismo', 'estado']
        for field in text_fields:
            if value := licitacion.get(field):
                cleaned_value = self._clean_text(value)
                if cleaned_value != value:
                    licitacion[field] = cleaned_value
                    diagnostics['suggestions'].append(f"Texto limpiado en {field}")

        # Verificación de campos de lista
        list_fields = ['requisitos', 'documentos', 'extractos']
        for field in list_fields:
            if field not in licitacion or not isinstance(licitacion[field], list):
                licitacion[field] = []
                diagnostics['suggestions'].append(f"Inicializado campo de lista: {field}")

        return diagnostics

    def _clean_text(self, text: str) -> str:
        """Limpiar texto eliminando espacios extra y caracteres no deseados"""
        if not text:
            return ""
        # Eliminar espacios extra, saltos de línea, etc.
        text = re.sub(r'\s+', ' ', text).strip()
        # Eliminar caracteres no imprimibles
        text = re.sub(r'[^\x20-\x7E\á\é\í\ó\ú\ñ\Á\É\Í\Ó\Ú\Ñ]', '', text)
        return text

    def diagnose_scraping_issues(self, licitaciones: List[Dict]) -> Dict:
        """
        Diagnosticar problemas en un conjunto de licitaciones
        """
        total_licitaciones = len(licitaciones)
        valid_licitaciones = []
        invalid_licitaciones = []

        for licitacion in licitaciones:
            diagnostics = self.validate_licitacion_comprehensive(licitacion)
            
            if diagnostics['is_valid']:
                valid_licitaciones.append(licitacion)
            else:
                invalid_licitaciones.append({
                    'licitacion': licitacion,
                    'diagnostics': diagnostics
                })

        return {
            'total_licitaciones': total_licitaciones,
            'valid_count': len(valid_licitaciones),
            'invalid_count': len(invalid_licitaciones),
            'valid_percentage': (len(valid_licitaciones) / total_licitaciones * 100) if total_licitaciones > 0 else 0,
            'valid_licitaciones': valid_licitaciones,
            'invalid_licitaciones': invalid_licitaciones
        }

def log_scraping_diagnostics(licitaciones: List[Dict]):
    """
    Función principal para realizar diagnóstico de scraping
    """
    diagnostics = ScrapingDiagnostics()
    result = diagnostics.diagnose_scraping_issues(licitaciones)

    # Logging detallado
    logging.info(f"Diagnóstico de Scraping:")
    logging.info(f"Total Licitaciones: {result['total_licitaciones']}")
    logging.info(f"Licitaciones Válidas: {result['valid_count']} ({result['valid_percentage']:.2f}%)")
    logging.info(f"Licitaciones Inválidas: {result['invalid_count']}")

    # Log de licitaciones inválidas
    if result['invalid_licitaciones']:
        logging.warning("Detalles de Licitaciones Inválidas:")
        for invalid in result['invalid_licitaciones']:
            logging.warning(f"Licitación Inválida: {invalid['licitacion'].get('titulo', 'Sin Título')}")
            logging.warning(f"Errores: {invalid['diagnostics']['errors']}")
            logging.warning(f"Advertencias: {invalid['diagnostics']['warnings']}")

    return result

# Ejemplo de uso
if __name__ == "__main__":
    # Ejemplo de uso del diagnóstico
    licitaciones_ejemplo = [
        {
            'titulo': 'Licitación de Prueba',
            'organismo': 'Ministerio de Pruebas',
            'estado': 'Activo',
            'fecha_publicacion': '2024-01-15'
        },
        {
            # Licitación con datos incompletos
            'titulo': '',
            'organismo': ''
        }
    ]

    diagnostics = log_scraping_diagnostics(licitaciones_ejemplo)
