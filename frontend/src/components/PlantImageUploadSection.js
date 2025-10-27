import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  IconButton,
  CircularProgress,
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import ImageIcon from '@mui/icons-material/Image';
import ImageUpload from './ImageUpload';

const PlantImageUploadSection = ({
  imagePreview,
  selectedImage,
  loading,
  onFileSelect,
  onRemoveImage,
  onQuickIdentify,
}) => {
  return (
    <Paper elevation={3} sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Plant Image
      </Typography>
      
      {!imagePreview ? (
        <ImageUpload
          onFileSelect={onFileSelect}
          selectedFile={selectedImage}
          preview={imagePreview}
          disabled={loading}
          minHeight={300}
        />
      ) : (
        <Box>
          <Box sx={{ position: 'relative' }}>
            <img
              src={imagePreview}
              alt="Plant"
              style={{
                width: '100%',
                maxHeight: 400,
                objectFit: 'contain',
                borderRadius: 8,
              }}
            />
            <IconButton
              sx={{
                position: 'absolute',
                top: 8,
                right: 8,
                bgcolor: 'background.paper',
                '&:hover': { bgcolor: 'error.light' },
              }}
              onClick={onRemoveImage}
              size="small"
            >
              <CloseIcon />
            </IconButton>
          </Box>
          
          <Button
            variant="contained"
            fullWidth
            onClick={onQuickIdentify}
            disabled={loading}
            sx={{ mt: 2 }}
            startIcon={loading ? <CircularProgress size={20} /> : <ImageIcon />}
          >
            {loading ? 'Analyzing...' : 'Identify This Plant'}
          </Button>

          <Typography variant="caption" display="block" sx={{ mt: 1, textAlign: 'center' }}>
            Or ask specific questions about this plant below
          </Typography>
        </Box>
      )}
    </Paper>
  );
};

export default PlantImageUploadSection;
