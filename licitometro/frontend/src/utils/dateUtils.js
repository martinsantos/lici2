export const formatDate = (dateString) => {
    if (!dateString) return '';
    try {
        const date = new Date(dateString);
        if (isNaN(date.getTime())) return ''; // Invalid date
        return date.toISOString().split('T')[0]; // Returns YYYY-MM-DD
    } catch (error) {
        console.error('Error formatting date:', error);
        return '';
    }
};

export const displayDate = (dateString) => {
    if (!dateString) return '';
    try {
        const date = new Date(dateString);
        if (isNaN(date.getTime())) return ''; // Invalid date
        return date.toLocaleDateString('es-AR', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    } catch (error) {
        console.error('Error formatting date for display:', error);
        return '';
    }
};
