import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

class ScraperEnhancer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

    def _normalizar_fecha(self, fecha: str) -> Optional[str]:
        """
        Normalizar y validar fechas con estrategias de recuperación avanzadas y múltiples mecanismos
        
        Args:
            fecha (str): Fecha a normalizar
        
        Returns:
            Optional[str]: Fecha normalizada en formato ISO o None
        """
        if not fecha or not isinstance(fecha, str):
            return None

        # Limpiar la entrada
        fecha = fecha.strip().lower().replace(' ', '')
        
        # Eliminar texto adicional como 'hrs.'
        fecha = re.sub(r'hrs\.?', '', fecha)

        # Patrones de fecha comprehensivos y tolerantes
        patrones = [
            r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})',   # dd/mm/yyyy o dd-mm-yyyy
            r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})',   # yyyy-mm-dd
            r'(\d{1,2})[/-](\d{1,2})[/-](\d{2})',   # dd/mm/yy
            r'(\d{1,2})\s*(?:de)?([a-zA-Z]+)\s*(?:de)?(\d{4})',  # dd de mes yyyy
            r'(\d{1,2})[.-](\d{1,2})[.-](\d{2,4})', # Soporte para separadores adicionales
        ]

        # Mapeo de meses en español
        meses_espanol = {
            'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4, 
            'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8, 
            'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
        }

        def parse_fecha(grupos):
            try:
                # Manejar patrón de texto de mes
                if len(grupos) == 3 and isinstance(grupos[1], str) and grupos[1].lower() in meses_espanol:
                    dia, mes_texto, año = grupos
                    mes = meses_espanol[mes_texto.lower()]
                    año = int(año)
                else:
                    # Otros patrones de fecha
                    if len(grupos[0]) == 4:  # yyyy-mm-dd
                        año, mes, dia = map(int, grupos)
                    elif len(grupos[2]) == 4:  # dd/mm/yyyy
                        dia, mes, año = map(int, grupos)
                    else:  # dd/mm/yy
                        dia, mes, año_corto = grupos
                        año = int(f"20{año_corto}" if int(año_corto) < 100 else año_corto)
                        mes, dia = int(mes), int(dia)

                # Estrategias de recuperación para años inválidos
                año_actual = datetime.now().year
                if año < 1900:
                    # Para años muy antiguos, asumir que es un error de formato
                    if año < 100:
                        año = año_actual - (100 - año)  # Ajuste para años de dos dígitos
                    else:
                        año = año_actual  # Usar año actual

                # Estrategias de recuperación para meses y días inválidos
                if mes > 12 or mes < 1:
                    # Intentar intercambiar mes y día
                    mes, dia = dia, mes

                # Ajustar mes si sigue inválido
                mes = max(1, min(mes, 12))

                # Ajustar día según el mes
                dias_por_mes = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
                dia = max(1, min(dia, dias_por_mes[mes-1]))

                # Validar fecha
                fecha_obj = datetime(año, mes, dia)
                
                # Validar rango de fechas razonable
                if fecha_obj.year > año_actual + 5:
                    # Si la fecha es muy futura, ajustar al año actual
                    fecha_obj = fecha_obj.replace(year=año_actual)

                return fecha_obj.strftime('%Y-%m-%d')
            except ValueError:
                return None

        # Intentar parsear con diferentes patrones
        for patron in patrones:
            match = re.search(patron, fecha, re.IGNORECASE)
            if match:
                resultado = parse_fecha(match.groups())
                if resultado:
                    return resultado

        # Estrategias de último recurso
        try:
            # Intentar parsear directamente con dateutil
            from dateutil.parser import parse
            fecha_parseada = parse(fecha, fuzzy=True)
            return fecha_parseada.strftime('%Y-%m-%d')
        except Exception:
            pass

        # Intentar extraer año, mes, día de manera más flexible
        numeros = re.findall(r'\d+', fecha)
        if len(numeros) >= 3:
            for i in range(len(numeros) - 2):
                # Probar diferentes combinaciones de año, mes, día
                combinaciones = [
                    (int(numeros[i]), int(numeros[i+1]), int(numeros[i+2])),
                    (int(numeros[i+2]), int(numeros[i]), int(numeros[i+1])),
                    (int(numeros[i+1]), int(numeros[i+2]), int(numeros[i]))
                ]
                
                for año, mes, dia in combinaciones:
                    # Ajustar años de dos dígitos
                    año_actual = datetime.now().year
                    if año < 100:
                        año = int(f"20{año}" if año < 100 else año)

                    # Ajustar meses y días
                    mes = max(1, min(mes, 12))
                    dias_por_mes = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
                    dia = max(1, min(dia, dias_por_mes[mes-1]))

                    try:
                        fecha_obj = datetime(año, mes, dia)
                        return fecha_obj.strftime('%Y-%m-%d')
                    except ValueError:
                        continue

        self.logger.warning(f"No se pudo parsear la fecha: {fecha}")
        return None

    def _inferir_fecha_publicacion(self, licitacion: Dict) -> str:
        """
        Inferir fecha de publicación con estrategias más comprehensivas
        
        Args:
            licitacion (Dict): Diccionario de licitación
        
        Returns:
            str: Fecha de publicación inferida
        """
        # Estrategias de inferencia de fecha de publicación
        estrategias = [
            # 1. Usar fecha de apertura si está disponible y es válida
            lambda: self._normalizar_fecha(licitacion.get('fecha_apertura')) if self._normalizar_fecha(licitacion.get('fecha_apertura')) else None,
            
            # 2. Extraer de la URL
            lambda: self._normalizar_fecha(self._extraer_fecha_de_url(licitacion.get('url_fuente', ''))),
            
            # 3. Extraer de la fecha en el título
            lambda: self._normalizar_fecha(self._extraer_fecha_de_texto(licitacion.get('titulo', ''))),
            
            # 4. Extraer de la fecha en el estado
            lambda: self._normalizar_fecha(self._extraer_fecha_de_texto(licitacion.get('estado', ''))),
            
            # 5. Fecha por defecto (15 días antes de hoy)
            lambda: (datetime.now() - timedelta(days=15)).strftime('%Y-%m-%d')
        ]

        for estrategia in estrategias:
            fecha = estrategia()
            if fecha:
                return fecha

        # Fecha final por defecto
        return (datetime.now() - timedelta(days=15)).strftime('%Y-%m-%d')

    def _extraer_fecha_de_url(self, url: str) -> Optional[str]:
        """
        Extraer fecha de la URL
        
        Args:
            url (str): URL a analizar
        
        Returns:
            Optional[str]: Fecha extraída o None
        """
        # Patrones de fecha en URL
        patrones_url = [
            r'\d{4}[-/]\d{2}[-/]\d{2}',  # yyyy-mm-dd o yyyy/mm/dd
            r'\d{2}[-/]\d{2}[-/]\d{4}',  # dd-mm-yyyy o dd/mm/yyyy
        ]
        
        for patron in patrones_url:
            match = re.search(patron, url)
            if match:
                return match.group()
        
        return None

    def _extraer_fecha_de_texto(self, texto: str) -> Optional[str]:
        """
        Extraer fecha de un texto
        
        Args:
            texto (str): Texto a analizar
        
        Returns:
            Optional[str]: Fecha extraída o None
        """
        # Patrones de fecha en texto
        patrones_texto = [
            r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',  # dd/mm/yyyy
            r'\d{4}[/-]\d{1,2}[/-]\d{1,2}',    # yyyy-mm-dd
            r'\d{1,2}\s*(?:de)?\s*[a-zA-Z]+\s*(?:de)?\s*\d{4}'  # dd de mes yyyy
        ]
        
        for patron in patrones_texto:
            match = re.search(patron, texto, re.IGNORECASE)
            if match:
                return match.group()
        
        return None

    def _normalizar_estado(self, estado: Optional[str], licitacion: Dict) -> Optional[str]:
        """
        Inferir y normalizar estado de la licitación con estrategias más comprehensivas
        
        Args:
            estado (Optional[str]): Estado original
            licitacion (Dict): Diccionario de licitación completo
        
        Returns:
            Optional[str]: Estado normalizado
        """
        # Diccionarios de normalización más flexibles
        estados_normalizados = {
            'en proceso': 'En Proceso',
            'publicado': 'Publicado',
            'pendiente': 'Pendiente',
            'activo': 'Activo',
            'abierto': 'Abierto',
            'cerrado': 'Cerrado',
            'adjudicado': 'Adjudicado',
            'convocatoria': 'En Proceso',
            'vigente': 'En Proceso',
            'finalizado': 'Cerrado'
        }

        # Normalizar estado si existe
        if estado:
            estado_lower = estado.lower().strip()
            
            # Buscar coincidencias parciales
            for key, value in estados_normalizados.items():
                if key in estado_lower:
                    return value
            
            # Si no hay coincidencia, devolver el estado original
            return estado.capitalize()

        # Estrategias de inferencia de estado más comprehensivas
        palabras_estado = {
            'En Proceso': ['convocatoria', 'abierta', 'vigente', 'activa', 'en curso', 'proceso', 'próxima'],
            'Publicado': ['publicada', 'publicado', 'disponible', 'lanzada', 'abierto'],
            'Pendiente': ['pendiente', 'futura', 'por iniciar'],
            'Cerrado': ['cerrada', 'finalizada', 'terminada', 'concluida'],
            'Adjudicado': ['adjudicada', 'ganador', 'asignada']
        }
        
        # Preparar texto completo para búsqueda
        titulo = licitacion.get('titulo', '').lower()
        organismo = licitacion.get('organismo', '').lower()
        estado_texto = licitacion.get('estado', '').lower()
        texto_completo = f"{titulo} {organismo} {estado_texto}"

        # Búsqueda de estado por palabras clave
        for estado_key, keywords in palabras_estado.items():
            if any(keyword in texto_completo for keyword in keywords):
                return estado_key

        # Inferencia por fecha de apertura
        fecha_apertura = licitacion.get('fecha_apertura')
        if fecha_apertura:
            try:
                fecha_obj = datetime.strptime(fecha_apertura, '%Y-%m-%d')
                if fecha_obj > datetime.now():
                    return 'En Proceso'
                elif fecha_obj <= datetime.now():
                    return 'Publicado'
            except ValueError:
                pass

        # Estado por defecto con más contexto
        return 'En Proceso'

    def _normalizar_monto(self, monto: Optional[float], moneda: Optional[str] = 'ARS') -> Optional[float]:
        """
        Normalizar y validar montos
        
        Args:
            monto (Optional[float]): Monto a normalizar
            moneda (Optional[str]): Moneda del monto
        
        Returns:
            Optional[float]: Monto normalizado o None
        """
        if monto is None or monto <= 0:
            return None
        
        # Conversión de moneda si es necesario (placeholder para futuras implementaciones)
        return round(monto, 2)

    def enrich_licitacion(self, licitacion: Dict) -> Dict:
        """
        Enriquecer y validar licitación con validación más comprehensiva y flexible
        
        Args:
            licitacion (Dict): Licitación a enriquecer
        
        Returns:
            Dict: Licitación enriquecida con validación
        """
        # Copia para no modificar el original
        licitacion_enriquecida = licitacion.copy()
        warnings = []

        # Campos obligatorios con mayor flexibilidad
        campos_obligatorios = ['titulo', 'url_fuente']
        
        # Validar campos obligatorios
        for campo in campos_obligatorios:
            if not licitacion_enriquecida.get(campo):
                warnings.append(f"Campo obligatorio faltante: {campo}")

        # Normalizar y validar fecha de apertura
        fecha_apertura = licitacion_enriquecida.get('fecha_apertura')
        fecha_normalizada = self._normalizar_fecha(fecha_apertura)
        if fecha_normalizada:
            licitacion_enriquecida['fecha_apertura'] = fecha_normalizada
        else:
            # Intentar inferir fecha de apertura de otros campos
            fecha_inferida = self._inferir_fecha_publicacion(licitacion_enriquecida)
            licitacion_enriquecida['fecha_apertura'] = fecha_inferida
            warnings.append("Fecha de apertura inferida por defecto")

        # Normalizar monto con validación más flexible
        monto = licitacion_enriquecida.get('monto')
        moneda = licitacion_enriquecida.get('moneda', 'ARS')
        monto_normalizado = self._normalizar_monto(monto, moneda)
        if monto_normalizado is not None:
            licitacion_enriquecida['monto'] = monto_normalizado
        else:
            # Establecer monto por defecto si no se puede normalizar
            licitacion_enriquecida['monto'] = 0.0
            warnings.append("Monto no válido, establecido en 0.0")

        # Normalizar estado con inferencia
        estado = licitacion_enriquecida.get('estado')
        estado_normalizado = self._normalizar_estado(estado, licitacion_enriquecida)
        licitacion_enriquecida['estado'] = estado_normalizado

        # Inferir fecha de publicación
        fecha_publicacion = licitacion_enriquecida.get('fecha_publicacion')
        if not fecha_publicacion:
            fecha_publicacion = self._inferir_fecha_publicacion(licitacion_enriquecida)
            licitacion_enriquecida['fecha_publicacion'] = fecha_publicacion
            warnings.append("Fecha de publicación inferida por defecto")

        # Registrar warnings
        if warnings:
            self.logger.warning(f"Licitación con advertencias: {warnings}")
            licitacion_enriquecida['warnings'] = warnings

        return licitacion_enriquecida

    def enrich_licitaciones(self, licitaciones: List[Dict]) -> List[Dict]:
        """
        Enriquecer múltiples licitaciones
        
        Args:
            licitaciones (List[Dict]): Lista de licitaciones
        
        Returns:
            List[Dict]: Lista de licitaciones enriquecidas
        """
        licitaciones_enriquecidas = []
        
        for licitacion in licitaciones:
            resultado = self.enrich_licitacion(licitacion)
            
            if resultado.get('warnings'):
                self.logger.warning(f"Licitación inválida: {resultado['warnings']}")
            else:
                licitaciones_enriquecidas.append(resultado)
        
        return licitaciones_enriquecidas

def get_logger(nombre: str) -> logging.Logger:
    """
    Obtener un logger con configuración básica
    
    Args:
        nombre (str): Nombre del logger
    
    Returns:
        logging.Logger: Logger configurado
    """
    logger = logging.getLogger(nombre)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

def enrich_licitaciones(licitaciones: List[Dict]) -> List[Dict]:
    """
    Función principal para enriquecer múltiples licitaciones
    """
    enhancer = ScraperEnhancer()
    licitaciones_enriquecidas = []
    
    for licitacion in licitaciones:
        resultado = enhancer.enrich_licitacion(licitacion)
        
        if resultado.get('warnings'):
            logging.warning(f"Licitación inválida: {resultado['warnings']}")
        else:
            licitaciones_enriquecidas.append(resultado)
    
    return licitaciones_enriquecidas

# Ejemplo de uso
if __name__ == "__main__":
    licitaciones_ejemplo = [
        {
            'titulo': 'adquisición de licencias de software microsoft',
            'url_fuente': 'https://comprar.gob.ar/Compras.aspx?qs=W1HXHGHtH10=',
            'organismo': '262/000 - dirección general de administración y finanzas - mad',
            'fecha_apertura': '29/11/2024'
        },
        {
            'titulo': 'adquisición de insumos descartables para laboratorio',
            'url_fuente': 'https://comprar.gob.ar/Compras.aspx?qs=W1HXHGHtH10=',
            'organismo': '67 - departamento de compras y contrataciones- incucai',
            'fecha_apertura': '29/11/2024'
        }
    ]

    licitaciones_procesadas = enrich_licitaciones(licitaciones_ejemplo)
    
    for licitacion in licitaciones_procesadas:
        print(licitacion)
