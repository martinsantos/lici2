/**
 * Formatea un tamaño de archivo en bytes a una representación legible
 * @param {number} bytes - Tamaño en bytes
 * @returns {string} Tamaño formateado (ej: "1.5 MB")
 */
export function formatFileSize(bytes) {
  if (!bytes || bytes === 0) return '0 B';
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`;
}

/**
 * Formatea un valor monetario con el símbolo de la moneda
 * @param {number} amount - Monto a formatear
 * @param {string} currency - Código de la moneda (ej: "ARS", "USD")
 * @returns {string} Monto formateado con símbolo de moneda
 */
export function formatCurrency(amount, currency = 'ARS') {
  const formatter = new Intl.NumberFormat('es-AR', {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  });
  return formatter.format(amount);
}

/**
 * Formatea una fecha ISO a un formato legible
 * @param {string} isoDate - Fecha en formato ISO
 * @returns {string} Fecha formateada
 */
export function formatDate(isoDate) {
  if (!isoDate) return '';
  return new Date(isoDate).toLocaleDateString('es-AR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
}

/**
 * Obtiene el color de estado para una licitación
 * @param {string} status - Estado de la licitación
 * @returns {Object} Objeto con clases de Tailwind para el color
 */
export function getStatusColor(status) {
  const colors = {
    'Abierta': {
      bg: 'bg-green-100',
      text: 'text-green-800'
    },
    'Cerrada': {
      bg: 'bg-red-100',
      text: 'text-red-800'
    },
    'En Evaluación': {
      bg: 'bg-yellow-100',
      text: 'text-yellow-800'
    },
    'Adjudicada': {
      bg: 'bg-blue-100',
      text: 'text-blue-800'
    },
    'Desierta': {
      bg: 'bg-gray-100',
      text: 'text-gray-800'
    }
  };
  
  return colors[status] || { bg: 'bg-gray-100', text: 'text-gray-800' };
}
