import React, { useState } from 'react';
import {
  Box,
  Typography,
  Button,
  CircularProgress,
  Alert,
  Card,
  CardContent,
  Grid,
  Chip,
  Divider,
  LinearProgress,
} from '@mui/material';
import ImageUpload from '../components/ImageUpload';
import { chatAPI, imageToFormData } from '../services/api';

const RecognitionPage = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  const handleFileSelect = (file) => {
    setSelectedFile(file);
    setPreview(URL.createObjectURL(file));
    setResults(null);
    setError(null);
  };

  const handleRecognize = async () => {
    if (!selectedFile) return;

    setLoading(true);
    setError(null);

    try {
      // Use chat-with-image endpoint for better RAG integration
      const formData = imageToFormData(selectedFile, {
        message: 'Please identify this plant and provide detailed information about it.',
        session_id: `recognition_${Date.now()}`,
      });

      const response = await chatAPI.sendImageMessage(formData);
      
      // Transform response to match expected format
      setResults({
        response: response.data.response,
        identified_plants: response.data.identified_plants || [],
        similarity_results: response.data.similarity_results || [],
        confidence: response.data.confidence || 0,
        timestamp: response.data.timestamp,
      });
    } catch (err) {
      setError(err.message || 'Failed to recognize plant. Please try again.');
      console.error('Recognition error:', err);
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
        Upload a plant image to identify the species and get detailed information powered by AI.
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <ImageUpload
            onFileSelect={handleFileSelect}
            selectedFile={selectedFile}
            preview={preview}
            disabled={loading}
            minHeight={350}
          />

          <Button
            variant="contained"
            size="large"
            fullWidth
            onClick={handleRecognize}
            disabled={!selectedFile || loading}
            sx={{ mt: 2 }}
          >
            {loading ? (
              <>
                <CircularProgress size={20} sx={{ mr: 1 }} color="inherit" />
                Analyzing...
              </>
            ) : (
              'Identify Plant'
            )}
          </Button>

          {loading && (
            <Box sx={{ mt: 2 }}>
              <LinearProgress />
              <Typography variant="caption" display="block" align="center" sx={{ mt: 1 }}>
                Processing image with AI... This may take a few seconds
              </Typography>
            </Box>
          )}
        </Grid>

        <Grid item xs={12} md={6}>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
              {error}
            </Alert>
          )}

          {results && (
            <Card elevation={3}>
              <CardContent>
                <Typography variant="h5" gutterBottom color="primary">
                  AI Analysis Result
                </Typography>

                <Divider sx={{ my: 2 }} />

                {/* Main Response */}
                <Box sx={{ mb: 3, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                  <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                    {results.response}
                  </Typography>
                </Box>

                {/* Confidence Score */}
                {results.confidence > 0 && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Confidence Score:
                    </Typography>
                    <Chip
                      label={`${(results.confidence * 100).toFixed(1)}%`}
                      color={results.confidence > 0.7 ? 'success' : results.confidence > 0.4 ? 'warning' : 'error'}
                      sx={{ fontWeight: 'bold' }}
                    />
                  </Box>
                )}

                {/* Identified Plants */}
                {results.identified_plants && results.identified_plants.length > 0 && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Identified Species:
                    </Typography>
                    {results.identified_plants.map((plant, idx) => (
                      <Chip
                        key={idx}
                        label={plant.scientificName || plant.scientific_name || plant.name}
                        sx={{ mr: 1, mb: 1 }}
                        variant="outlined"
                        color="primary"
                      />
                    ))}
                  </Box>
                )}

                {/* Similar Plants from Vector DB */}
                {results.similarity_results && results.similarity_results.length > 0 && (
                  <Box>
                    <Typography variant="subtitle2" gutterBottom>
                      Similar Plants (Vector DB):
                    </Typography>
                    {results.similarity_results.map((result, idx) => (
                      <Box
                        key={idx}
                        sx={{
                          p: 1.5,
                          mb: 1,
                          bgcolor: 'background.paper',
                          border: '1px solid',
                          borderColor: 'divider',
                          borderRadius: 1,
                        }}
                      >
                        <Typography variant="body2" fontWeight="medium">
                          {result.scientificName || result.name}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Similarity: {(result.distance * 100).toFixed(1)}%
                        </Typography>
                      </Box>
                    ))}
                  </Box>
                )}

                <Divider sx={{ my: 2 }} />

                <Typography variant="caption" color="text.secondary" display="block">
                  Analysis completed at {new Date(results.timestamp).toLocaleString()}
                </Typography>
              </CardContent>
            </Card>
          )}
        </Grid>
      </Grid>
    </Box>
  );
};

export default RecognitionPage;
