// Helper for getting file names safely
export const getFileName = (doc: any): string => {
  if (!doc) return 'Documento';
  if (typeof doc === 'string') {
    try {
      const parts = doc.split('/');
      return parts[parts.length - 1].replace(/^\d+-/, '') || 'Documento';
    } catch (e) {
      console.error('Error parsing filename:', e);
      return 'Documento';
    }
  }
  if (typeof doc === 'object' && doc !== null) {
    if (doc.nombre) return doc.nombre;
    if (doc.path) {
      try {
        const parts = doc.path.split('/');
        return parts[parts.length - 1].replace(/^\d+-/, '') || 'Documento';
      } catch (e) {
        console.error('Error parsing filename from path:', e);
        return 'Documento';
      }
    }
  }
  return 'Documento';
};

// Helper for getting file URLs safely
export const getFileUrl = (doc: any): string => {
  if (!doc) return '';
  if (typeof doc === 'string') return doc;
  if (typeof doc === 'object' && doc !== null) {
    return doc.path || '';
  }
  return '';
};
