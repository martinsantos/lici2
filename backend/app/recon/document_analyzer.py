import pytesseract
from pdf2image import convert_from_path
import docx2txt
import pandas as pd
from typing import Dict, Any, List, Optional
import os
import tempfile
import json
import logging
import shutil

logger = logging.getLogger(__name__)

class DocumentAnalyzer:
    def __init__(self, plantilla: Dict[str, Any]):
        self.plantilla = plantilla
        self.reglas = plantilla.get('reglas', {})
        self.mapeo = plantilla.get('mapeo', {})
        self._verificar_dependencias()
    
    def _verificar_dependencias(self) -> None:
        """Verifica que las dependencias necesarias estén instaladas."""
        # Verificar Tesseract
        if not shutil.which('tesseract'):
            logger.error("Tesseract no está instalado en el sistema")
            raise RuntimeError("Tesseract OCR no está instalado. Por favor, instale Tesseract OCR para procesar documentos PDF.")
        
        # Verificar Poppler
        try:
            from pdf2image.exceptions import PDFPageCountError
        except ImportError:
            logger.error("Poppler no está instalado correctamente")
            raise RuntimeError("Poppler no está instalado. Por favor, instale Poppler para procesar documentos PDF.")
    
    def analizar_documento(self, ruta_documento: str) -> Dict[str, Any]:
        """Analiza un documento según la plantilla configurada."""
        extension = os.path.splitext(ruta_documento)[1].lower()
        texto = self.extraer_texto(ruta_documento, extension)
        
        if not texto:
            return {
                'estado': 'error',
                'mensaje': 'No se pudo extraer texto del documento'
            }
        
        # Aplicar reglas de extracción
        resultados = self.aplicar_reglas(texto)
        
        # Validar resultados
        resultados_validados = self.validar_resultados(resultados)
        
        return {
            'estado': 'completado',
            'resultados': resultados_validados,
            'texto_extraido': texto[:1000]  # Primeros 1000 caracteres para referencia
        }
    
    def extraer_texto(self, ruta_documento: str, extension: str) -> Optional[str]:
        """Extrae texto de diferentes tipos de documentos."""
        try:
            if extension == '.pdf':
                return self.extraer_texto_pdf(ruta_documento)
            elif extension == '.docx':
                return docx2txt.process(ruta_documento)
            elif extension in ['.xlsx', '.xls']:
                return self.extraer_texto_excel(ruta_documento)
            else:
                return None
        except Exception as e:
            logger.error(f"Error extrayendo texto: {str(e)}")
            return None
    
    def extraer_texto_pdf(self, ruta_pdf: str) -> str:
        """Extrae texto de un PDF usando OCR si es necesario."""
        try:
            # Convertir PDF a imágenes
            with tempfile.TemporaryDirectory() as temp_dir:
                try:
                    imagenes = convert_from_path(ruta_pdf)
                except Exception as e:
                    logger.error(f"Error al convertir PDF a imágenes: {str(e)}")
                    raise RuntimeError(f"No se pudo procesar el PDF: {str(e)}")
                
                texto_completo = []
                
                for i, imagen in enumerate(imagenes):
                    try:
                        # Usar OCR para extraer texto
                        texto = pytesseract.image_to_string(imagen, lang='spa')
                        texto_completo.append(texto)
                        logger.debug(f"Procesada página {i+1} de {len(imagenes)}")
                    except Exception as e:
                        logger.error(f"Error en OCR de página {i+1}: {str(e)}")
                        continue
                
                if not texto_completo:
                    raise RuntimeError("No se pudo extraer texto de ninguna página del PDF")
                
                return '\n'.join(texto_completo)
        except Exception as e:
            logger.error(f"Error general procesando PDF: {str(e)}")
            raise
    
    def extraer_texto_excel(self, ruta_excel: str) -> str:
        """Extrae texto de un archivo Excel."""
        try:
            # Intentar leer todas las hojas del archivo Excel
            excel_file = pd.ExcelFile(ruta_excel)
            texto_completo = []
            
            for nombre_hoja in excel_file.sheet_names:
                try:
                    df = pd.read_excel(excel_file, sheet_name=nombre_hoja)
                    # Convertir todas las columnas a string para mejor manejo
                    df = df.astype(str)
                    # Eliminar valores NaN y concatenar el contenido
                    texto_hoja = df.apply(lambda x: ' '.join(x.dropna()), axis=1).str.cat(sep='\n')
                    texto_completo.append(f"=== Hoja: {nombre_hoja} ===\n{texto_hoja}")
                    logger.debug(f"Procesada hoja '{nombre_hoja}' exitosamente")
                except Exception as e:
                    logger.error(f"Error procesando hoja '{nombre_hoja}': {str(e)}")
                    continue
            
            if not texto_completo:
                raise RuntimeError("No se pudo extraer texto de ninguna hoja del archivo Excel")
            
            return '\n\n'.join(texto_completo)
            
        except Exception as e:
            logger.error(f"Error procesando archivo Excel: {str(e)}")
            raise RuntimeError(f"Error al procesar el archivo Excel: {str(e)}")

    def aplicar_reglas(self, texto: str) -> Dict[str, Any]:
        """Aplica las reglas de extracción definidas en la plantilla."""
        try:
            resultados = {}
            
            for campo, reglas in self.reglas.get('extraccion', {}).items():
                try:
                    valor = None
                    patron = reglas.get('patron')
                    
                    if patron:
                        import re
                        match = re.search(patron, texto, re.MULTILINE | re.IGNORECASE)
                        if match:
                            valor = match.group(1) if match.groups() else match.group(0)
                    
                    # Aplicar transformaciones si existen
                    if valor and 'transformaciones' in reglas:
                        valor = self.aplicar_transformaciones(valor, reglas['transformaciones'])
                    
                    if valor:
                        resultados[campo] = valor
                        logger.debug(f"Campo '{campo}' extraído exitosamente")
                    else:
                        logger.warning(f"No se pudo extraer el campo '{campo}'")
                
                except Exception as e:
                    logger.error(f"Error procesando campo '{campo}': {str(e)}")
                    continue
            
            return self.validar_resultados(resultados)
            
        except Exception as e:
            logger.error(f"Error aplicando reglas de extracción: {str(e)}")
            raise RuntimeError(f"Error al aplicar reglas de extracción: {str(e)}")
    
    def validar_resultados(self, resultados: Dict[str, Any]) -> Dict[str, Any]:
        """Valida los resultados según las reglas definidas."""
        try:
            validados = {}
            
            for campo, valor in resultados.items():
                try:
                    if campo not in self.reglas.get('validaciones', {}):
                        validados[campo] = valor
                        continue
                        
                    reglas = self.reglas['validaciones'][campo]
                    
                    # Validar obligatorio
                    if reglas.get('obligatorio', False) and not valor:
                        logger.error(f"Campo obligatorio '{campo}' está vacío")
                        continue
                    
                    # Validar tipo
                    tipo = reglas.get('tipo')
                    if tipo:
                        try:
                            if tipo == 'numero':
                                valor = float(str(valor).replace(',', '').strip())
                            elif tipo == 'fecha':
                                from datetime import datetime
                                valor = datetime.strptime(valor, reglas.get('formato_fecha', '%Y-%m-%d'))
                            elif tipo == 'texto':
                                valor = str(valor).strip()
                        except Exception as e:
                            logger.error(f"Error validando tipo de dato para campo '{campo}': {str(e)}")
                            continue
                    
                    # Validar rango
                    if 'rango' in reglas and tipo == 'numero':
                        min_val, max_val = reglas['rango']
                        if not (min_val <= float(valor) <= max_val):
                            logger.error(f"Valor fuera de rango para campo '{campo}': {valor}")
                            continue
                    
                    # Validar longitud
                    if 'longitud' in reglas and tipo == 'texto':
                        min_len, max_len = reglas['longitud']
                        if not (min_len <= len(str(valor)) <= max_len):
                            logger.error(f"Longitud inválida para campo '{campo}': {len(str(valor))}")
                            continue
                    
                    # Validar formato
                    if 'formato' in reglas:
                        if not self.validar_formato(valor, reglas['formato']):
                            logger.error(f"Formato inválido para campo '{campo}': {valor}")
                            continue
                    
                    validados[campo] = valor
                    logger.debug(f"Campo '{campo}' validado exitosamente")
                    
                except Exception as e:
                    logger.error(f"Error validando campo '{campo}': {str(e)}")
                    continue
            
            return validados
            
        except Exception as e:
            logger.error(f"Error en validación de resultados: {str(e)}")
            raise RuntimeError(f"Error al validar resultados: {str(e)}")
    
    def validar_formato(self, valor: str, formato: str) -> bool:
        """Valida si un valor cumple con un formato específico usando expresiones regulares."""
        try:
            import re
            return bool(re.match(formato, str(valor)))
        except Exception as e:
            logger.error(f"Error validando formato: {str(e)}")
            return False
    
    def aplicar_transformaciones(self, valor: str, transformaciones: List[Dict[str, Any]]) -> Any:
        """Aplica transformaciones a un valor extraído."""
        try:
            for trans in transformaciones:
                try:
                    tipo = trans.get('tipo')
                    if tipo == 'fecha':
                        from datetime import datetime
                        valor = datetime.strptime(valor, trans['formato'])
                    elif tipo == 'numero':
                        valor = float(str(valor).replace(',', '').replace('$', '').strip())
                    elif tipo == 'texto':
                        valor = str(valor).strip()
                        if 'mayusculas' in trans:
                            valor = valor.upper() if trans['mayusculas'] else valor.lower()
                        if 'remover_espacios' in trans:
                            valor = ''.join(valor.split())
                    logger.debug(f"Transformación '{tipo}' aplicada exitosamente")
                except Exception as e:
                    logger.error(f"Error aplicando transformación '{tipo}': {str(e)}")
                    continue
            
            return valor
            
        except Exception as e:
            logger.error(f"Error en transformación de valor: {str(e)}")
            raise RuntimeError(f"Error al transformar valor: {str(e)}")
