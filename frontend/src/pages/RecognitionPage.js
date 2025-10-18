import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  CircularProgress,
  Alert,
  Card,
  CardContent,
  CardMedia,
  Grid,
  Chip,
} from '@mui/material';
import { useDropzone } from 'react-dropzone';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import axios from 'axios';

const RecognitionPage = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  const onDrop = (acceptedFiles) => {
    const file = acceptedFiles[0];
    if (file) {
      setSelectedFile(file);
      setPreview(URL.createObjectURL(file));
      setResults(null);
      setError(null);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png']
    },
    multiple: false,
  });

  const handleRecognize = async () => {
    if (!selectedFile) return;

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await axios.post('/api/v1/recognize', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setResults(response.data.results);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to recognize plant');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Plant Image Recognition
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Upload a plant image to identify the species and get detailed information.
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper
            {...getRootProps()}
            sx={{
              p: 4,
              textAlign: 'center',
              cursor: 'pointer',
              border: '2px dashed',
              borderColor: isDragActive ? 'primary.main' : 'grey.300',
              bgcolor: isDragActive ? 'action.hover' : 'background.paper',
              minHeight: 300,
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'center',
              alignItems: 'center',
            }}
          >
            <input {...getInputProps()} />
            {preview ? (
              <Box>
                <img
                  src={preview}
                  alt="Preview"
                  style={{ maxWidth: '100%', maxHeight: 250, borderRadius: 8 }}
                />
                <Typography variant="body2" sx={{ mt: 2 }}>
                  {selectedFile.name}
                </Typography>
              </Box>
            ) : (
              <>
                <CloudUploadIcon sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  {isDragActive ? 'Drop the image here' : 'Drag & drop a plant image'}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  or click to select a file
                </Typography>
              </>
            )}
          </Paper>

          <Button
            variant="contained"
            size="large"
            fullWidth
            onClick={handleRecognize}
            disabled={!selectedFile || loading}
            sx={{ mt: 2 }}
          >
            {loading ? <CircularProgress size={24} /> : 'Recognize Plant'}
          </Button>
        </Grid>

        <Grid item xs={12} md={6}>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          {results && (
            <Card elevation={3}>
              <CardContent>
                <Typography variant="h5" gutterBottom>
                  Recognition Results
                </Typography>

                {results.combined_results && (
                  <Box sx={{ mb: 3 }}>
                    <Typography variant="h6" color="primary">
                      {results.combined_results.scientific_name}
                    </Typography>
                    <Typography variant="subtitle1" color="text.secondary" gutterBottom>
                      {results.combined_results.common_name}
                    </Typography>
                    {results.combined_results.family && (
                      <Chip
                        label={`Family: ${results.combined_results.family}`}
                        size="small"
                        sx={{ mr: 1 }}
                      />
                    )}
                    <Chip
                      label={`Confidence: ${(results.combined_results.confidence * 100).toFixed(1)}%`}
                      color="primary"
                      size="small"
                    />
                  </Box>
                )}

                {results.description && (
                  <Paper elevation={1} sx={{ p: 2, bgcolor: 'grey.50' }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Description:
                    </Typography>
                    <Typography variant="body2">
                      {results.description}
                    </Typography>
                  </Paper>
                )}

                {results.plantnet_results?.results && (
                  <Box sx={{ mt: 3 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Alternative Matches:
                    </Typography>
                    {results.plantnet_results.results.slice(1, 4).map((result, idx) => (
                      <Paper key={idx} elevation={0} sx={{ p: 1, mb: 1, bgcolor: 'grey.50' }}>
                        <Typography variant="body2">
                          {result.scientific_name} - {(result.score * 100).toFixed(1)}%
                        </Typography>
                      </Paper>
                    ))}
                  </Box>
                )}
              </CardContent>
            </Card>
          )}
        </Grid>
      </Grid>
    </Box>
  );
};

export default RecognitionPage;
