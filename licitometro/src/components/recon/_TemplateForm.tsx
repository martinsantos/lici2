import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  TextField,
  Typography,
  Paper,
  IconButton,
  Grid,
  FormControlLabel,
  Checkbox,
  MenuItem,
} from '@mui/material';
import { Delete as DeleteIcon, Add as AddIcon } from '@mui/icons-material';
import { ScrapingTemplate, TemplateField } from '../../types/recon';

interface Props {
  template: ScrapingTemplate | null;
  onSubmit: (template: ScrapingTemplate) => void;
  onCancel: () => void;
}

const FIELD_TYPES = [
  { value: 'text', label: 'Texto' },
  { value: 'date', label: 'Fecha' },
  { value: 'number', label: 'Número' },
  { value: 'url', label: 'URL' },
  { value: 'html', label: 'HTML' },
];

const DEFAULT_FIELD: TemplateField = {
  name: '',
  selector: '',
  type: 'text',
  required: false,
};

const TemplateForm: React.FC<Props> = ({ template, onSubmit, onCancel }) => {
  const [formData, setFormData] = useState<ScrapingTemplate>({
    name: '',
    url: '',
    description: '',
    fields: [{ ...DEFAULT_FIELD }],
  });

  useEffect(() => {
    if (template) {
      setFormData(template);
    }
  }, [template]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleFieldChange = (index: number, field: string, value: any) => {
    setFormData((prev) => {
      const newFields = [...prev.fields];
      newFields[index] = {
        ...newFields[index],
        [field]: value,
      };
      return { ...prev, fields: newFields };
    });
  };

  const addField = () => {
    setFormData((prev) => ({
      ...prev,
      fields: [...prev.fields, { ...DEFAULT_FIELD }],
    }));
  };

  const removeField = (index: number) => {
    setFormData((prev) => ({
      ...prev,
      fields: prev.fields.filter((_, i) => i !== index),
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <Paper sx={{ p: 2 }}>
      <form onSubmit={handleSubmit}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom>
              {template ? 'Editar Template' : 'Nuevo Template'}
            </Typography>
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              required
              label="Nombre"
              name="name"
              value={formData.name}
              onChange={handleChange}
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              required
              label="URL"
              name="url"
              value={formData.url}
              onChange={handleChange}
            />
          </Grid>

          <Grid item xs={12}>
            <TextField
              fullWidth
              multiline
              rows={2}
              label="Descripción"
              name="description"
              value={formData.description}
              onChange={handleChange}
            />
          </Grid>

          <Grid item xs={12}>
            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle1" gutterBottom>
                Campos
              </Typography>
              {formData.fields.map((field, index) => (
                <Box
                  key={index}
                  sx={{
                    p: 2,
                    mb: 2,
                    border: '1px solid #e0e0e0',
                    borderRadius: 1,
                  }}
                >
                  <Grid container spacing={2} alignItems="center">
                    <Grid item xs={12} sm={3}>
                      <TextField
                        fullWidth
                        required
                        label="Nombre del Campo"
                        value={field.name}
                        onChange={(e) =>
                          handleFieldChange(index, 'name', e.target.value)
                        }
                      />
                    </Grid>
                    <Grid item xs={12} sm={3}>
                      <TextField
                        fullWidth
                        required
                        label="Selector"
                        value={field.selector}
                        onChange={(e) =>
                          handleFieldChange(index, 'selector', e.target.value)
                        }
                      />
                    </Grid>
                    <Grid item xs={12} sm={2}>
                      <TextField
                        fullWidth
                        required
                        select
                        label="Tipo"
                        value={field.type}
                        onChange={(e) =>
                          handleFieldChange(index, 'type', e.target.value)
                        }
                      >
                        {FIELD_TYPES.map((option) => (
                          <MenuItem key={option.value} value={option.value}>
                            {option.label}
                          </MenuItem>
                        ))}
                      </TextField>
                    </Grid>
                    <Grid item xs={12} sm={3}>
                      <FormControlLabel
                        control={
                          <Checkbox
                            checked={field.required}
                            onChange={(e) =>
                              handleFieldChange(index, 'required', e.target.checked)
                            }
                          />
                        }
                        label="Requerido"
                      />
                    </Grid>
                    <Grid item xs={12} sm={1}>
                      <IconButton
                        color="error"
                        onClick={() => removeField(index)}
                        disabled={formData.fields.length === 1}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </Grid>
                  </Grid>
                </Box>
              ))}
              <Button
                startIcon={<AddIcon />}
                onClick={addField}
                variant="outlined"
                sx={{ mt: 1 }}
              >
                Agregar Campo
              </Button>
            </Box>
          </Grid>

          <Grid item xs={12}>
            <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
              <Button variant="outlined" onClick={onCancel}>
                Cancelar
              </Button>
              <Button variant="contained" type="submit">
                {template ? 'Guardar Cambios' : 'Crear Template'}
              </Button>
            </Box>
          </Grid>
        </Grid>
      </form>
    </Paper>
  );
};

export default TemplateForm;
