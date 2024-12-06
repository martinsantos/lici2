import React from 'react';
import { Documento } from '../types';
import DocumentService from '../services/documentService';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import IconButton from '@mui/material/IconButton';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import DeleteIcon from '@mui/icons-material/Delete';
import DescriptionIcon from '@mui/icons-material/Description';

interface DocumentListProps {
  documents: Documento[];
  onDelete?: (documentId: number) => void;
}

const DocumentList: React.FC<DocumentListProps> = ({ documents, onDelete }) => {
  const documentService = DocumentService.getInstance();

  const handleDelete = async (documentId: number) => {
    if (onDelete) {
      onDelete(documentId);
    }
  };

  return (
    <List>
      {documents.map((doc) => (
        <ListItem
          key={doc.id}
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            border: '1px solid #e0e0e0',
            borderRadius: '4px',
            mb: 1,
            p: 2,
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', flex: 1 }}>
            <DescriptionIcon sx={{ mr: 2 }} />
            <Box>
              <a
                href={documentService.getDocumentUrl(doc)}
                target="_blank"
                rel="noopener noreferrer"
                style={{ textDecoration: 'none', color: 'inherit' }}
                onClick={(e) => {
                  if (!doc.id) {
                    e.preventDefault();
                    console.error('Document ID is missing');
                  }
                }}
              >
                <Typography variant="body1" component="span">
                  {doc.nombre}
                </Typography>
              </a>
              <Typography variant="body2" color="textSecondary">
                {new Date(doc.fecha_subida).toLocaleDateString()}
              </Typography>
            </Box>
          </Box>
          
          {onDelete && (
            <IconButton
              onClick={() => handleDelete(doc.id)}
              color="error"
              size="small"
            >
              <DeleteIcon />
            </IconButton>
          )}
        </ListItem>
      ))}
    </List>
  );
};

export default DocumentList;
