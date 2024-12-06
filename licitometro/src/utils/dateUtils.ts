export const formatDate = (dateString: string | Date | undefined | null): string => {
  if (!dateString) return '';
  try {
    const date = typeof dateString === 'string' ? new Date(dateString) : dateString;
    return date.toLocaleDateString('es-AR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    }).replace(/\//g, '/');
  } catch (e) {
    console.error('Error formatting date:', e);
    return '';
  }
};

export const formatDateForInput = (date: string | Date | undefined | null): string => {
  if (!date) return '';
  try {
    const d = new Date(date);
    if (isNaN(d.getTime())) return '';
    return d.toISOString().split('T')[0];
  } catch (e) {
    console.error('Error formatting date for input:', e);
    return '';
  }
};
