import React from 'react';
import { Box, Paper, Typography } from '@mui/material';
import { useDropzone } from 'react-dropzone';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';

/**
 * Reusable image upload component with drag-and-drop support
 * 
 * @param {Object} props
 * @param {Function} props.onFileSelect - Callback when file is selected
 * @param {File} props.selectedFile - Currently selected file
 * @param {string} props.preview - Preview URL of the image
 * @param {boolean} props.disabled - Whether the upload is disabled
 * @param {number} props.minHeight - Minimum height of the upload area
 * @param {boolean} props.showPreview - Whether to show image preview
 */
const ImageUpload = ({
  onFileSelect,
  selectedFile,
  preview,
  disabled = false,
  minHeight = 300,
  showPreview = true,
}) => {
  const onDrop = (acceptedFiles) => {
    const file = acceptedFiles[0];
    if (file && onFileSelect) {
      onFileSelect(file);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.gif', '.webp']
    },
    multiple: false,
    disabled,
  });

  return (
    <Paper
      {...getRootProps()}
      sx={{
        p: 4,
        textAlign: 'center',
        cursor: disabled ? 'not-allowed' : 'pointer',
        border: '2px dashed',
        borderColor: isDragActive ? 'primary.main' : 'grey.300',
        bgcolor: isDragActive ? 'action.hover' : disabled ? 'action.disabledBackground' : 'background.paper',
        minHeight,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        transition: 'all 0.2s ease-in-out',
        '&:hover': disabled ? {} : {
          borderColor: 'primary.main',
          bgcolor: 'action.hover',
        },
      }}
    >
      <input {...getInputProps()} />
      
      {showPreview && preview ? (
        <Box sx={{ width: '100%' }}>
          <img
            src={preview}
            alt="Preview"
            style={{
              maxWidth: '100%',
              maxHeight: minHeight - 80,
              borderRadius: 8,
              objectFit: 'contain',
            }}
          />
          {selectedFile && (
            <Typography variant="body2" sx={{ mt: 2 }} color="text.secondary">
              {selectedFile.name}
            </Typography>
          )}
          <Typography variant="caption" display="block" color="text.secondary" sx={{ mt: 1 }}>
            Click or drag to replace
          </Typography>
        </Box>
      ) : (
        <>
          <CloudUploadIcon 
            sx={{ 
              fontSize: 64, 
              color: disabled ? 'action.disabled' : 'primary.main', 
              mb: 2 
            }} 
          />
          <Typography variant="h6" gutterBottom>
            {isDragActive 
              ? 'Drop the image here' 
              : 'Drag & drop a plant image'}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            or click to select a file
          </Typography>
          <Typography variant="caption" color="text.secondary" sx={{ mt: 1 }}>
            Supported formats: JPEG, PNG, GIF, WebP
          </Typography>
        </>
      )}
    </Paper>
  );
};

export default ImageUpload;
