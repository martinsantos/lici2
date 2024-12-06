import React from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Tooltip,
  Typography,
} from '@mui/material';
import {
  Edit as EditIcon,
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { ScrapingTemplate } from '../../types/recon';

interface Props {
  templates: ScrapingTemplate[];
  onEdit: (template: ScrapingTemplate) => void;
  onRefresh: () => void;
}

const TemplateList: React.FC<Props> = ({ templates, onEdit, onRefresh }) => {
  const handleDelete = async (id: string) => {
    if (!window.confirm('¿Estás seguro de que quieres eliminar este template?')) {
      return;
    }

    try {
      const response = await fetch(`/api/templates/${id}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        onRefresh();
      }
    } catch (error) {
      console.error('Error deleting template:', error);
    }
  };

  return (
    <Paper sx={{ width: '100%', overflow: 'hidden' }}>
      <TableContainer sx={{ maxHeight: 440 }}>
        <Table stickyHeader>
          <TableHead>
            <TableRow>
              <TableCell>Nombre</TableCell>
              <TableCell>URL</TableCell>
              <TableCell>Descripción</TableCell>
              <TableCell>Campos</TableCell>
              <TableCell>Última Actualización</TableCell>
              <TableCell align="right">Acciones</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {templates.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} align="center">
                  <Typography variant="body2" color="textSecondary">
                    No hay templates disponibles
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              templates.map((template) => (
                <TableRow key={template.id}>
                  <TableCell>{template.name}</TableCell>
                  <TableCell>{template.url}</TableCell>
                  <TableCell>{template.description}</TableCell>
                  <TableCell>{template.fields.length} campos</TableCell>
                  <TableCell>
                    {template.updatedAt
                      ? new Date(template.updatedAt).toLocaleDateString()
                      : 'N/A'}
                  </TableCell>
                  <TableCell align="right">
                    <Tooltip title="Editar">
                      <IconButton
                        size="small"
                        onClick={() => onEdit(template)}
                      >
                        <EditIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Eliminar">
                      <IconButton
                        size="small"
                        onClick={() => template.id && handleDelete(template.id)}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Paper>
  );
};

export default TemplateList;
