import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  IconButton,
  Button,
  Grid,
  Card,
  CardContent,
  Chip,
  Divider,
  Alert,
  CircularProgress,
  Avatar,
  List,
  ListItem,
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import PersonIcon from '@mui/icons-material/Person';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import AttachFileIcon from '@mui/icons-material/AttachFile';
import CloseIcon from '@mui/icons-material/Close';
import ImageIcon from '@mui/icons-material/Image';
import ImageUpload from '../components/ImageUpload';
import { chatAPI, imageToFormData } from '../services/api';

// Generate a simple session ID
const generateSessionId = () => {
  return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
};

const InteractivePlantPage = () => {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: '👋 Hello! I\'m your botanical assistant. You can:\n\n• Upload a plant image to identify it\n• Ask questions about plants\n• Upload an image and ask specific questions about it\n\nHow can I help you today?',
      timestamp: new Date().toISOString(),
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId] = useState(() => generateSessionId());
  
  // Image states
  const [selectedImage, setSelectedImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [currentPlantContext, setCurrentPlantContext] = useState(null);
  
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleFileSelect = (file) => {
    setSelectedImage(file);
    setImagePreview(URL.createObjectURL(file));
  };

  const handleRemoveImage = () => {
    setSelectedImage(null);
    setImagePreview(null);
    setCurrentPlantContext(null);
  };

  const handleQuickIdentify = async () => {
    if (!selectedImage) return;
    
    // Auto-send identification request
    await handleSend('Please identify this plant and provide detailed information about it.');
  };

  const handleSend = async (customMessage = null) => {
    const messageText = customMessage || input;
    if (!messageText.trim() && !selectedImage) return;

    const userMessage = {
      role: 'user',
      content: messageText,
      timestamp: new Date().toISOString(),
      hasImage: !!selectedImage,
      imageName: selectedImage ? selectedImage.name : null,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      let response;

      if (selectedImage) {
        // Chat with image
        const formData = imageToFormData(selectedImage, {
          message: messageText || 'Please identify this plant and provide information about it.',
          session_id: sessionId,
        });

        response = await chatAPI.sendImageMessage(formData);
        
        // Save plant context for follow-up questions
        if (response.data.identified_plants && response.data.identified_plants.length > 0) {
          setCurrentPlantContext({
            plants: response.data.identified_plants,
            image: imagePreview,
            timestamp: response.data.timestamp,
          });
        }
        
        // Keep image for follow-up questions unless user removes it
        // setSelectedImage(null);
        // setImagePreview(null);
      } else {
        // Text-only chat (might reference previous plant context)
        let contextMessage = messageText;
        if (currentPlantContext) {
          const plantNames = currentPlantContext.plants
            .map(p => p.scientificName || p.scientific_name)
            .join(', ');
          contextMessage = `Regarding the previously identified plants (${plantNames}): ${messageText}`;
        }

        response = await chatAPI.sendMessage({
          message: contextMessage,
          session_id: sessionId,
          conversation_history: messages
            .filter((m) => !m.error)
            .map(({ role, content }) => ({ role, content })),
        });
      }

      const assistantMessage = {
        role: 'assistant',
        content: response.data.response,
        timestamp: response.data.timestamp,
        plants: response.data.identified_plants || response.data.relevant_plants || [],
        confidence: response.data.highest_confidence || response.data.confidence,
        total_matches: response.data.total_matches,
        similarity_results: response.data.similarity_results,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage = {
        role: 'assistant',
        content: error.message || 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString(),
        error: true,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <Box sx={{ position: 'relative', minHeight: 'calc(100vh - 200px)' }}>
      {/* Background for this page */}
      <Box
        sx={{
          position: 'absolute',
          top: -100,
          left: -100,
          right: -100,
          bottom: -100,
          zIndex: -1,
          pointerEvents: 'none',
          background: `
            radial-gradient(ellipse at 30% 20%, rgba(147, 51, 234, 0.08) 0%, transparent 40%),
            radial-gradient(ellipse at 70% 80%, rgba(45, 106, 79, 0.12) 0%, transparent 40%)
          `,
        }}
      />
      
      <Typography 
        variant="h4" 
        component="h1" 
        gutterBottom
        sx={{
          fontWeight: 700,
          display: 'flex',
          alignItems: 'center',
          gap: 1,
        }}
      >
        🌿 Interactive Plant Assistant
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Upload plant images, ask questions, and get instant AI-powered botanical insights
      </Typography>

      <Grid container spacing={3}>
        {/* Left Side - Image Upload & Context */}
        <Grid item xs={12} md={5}>
          <Paper elevation={3} sx={{ p: 2, mb: 2 }}>
            <Typography variant="h6" gutterBottom>
              Plant Image
            </Typography>
            
            {!imagePreview ? (
              <ImageUpload
                onFileSelect={handleFileSelect}
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
                    onClick={handleRemoveImage}
                    size="small"
                  >
                    <CloseIcon />
                  </IconButton>
                </Box>
                
                <Button
                  variant="contained"
                  fullWidth
                  onClick={handleQuickIdentify}
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

          {/* Current Plant Context */}
          {currentPlantContext && (
            <Card elevation={2}>
              <CardContent>
                <Typography variant="subtitle2" gutterBottom color="primary">
                  Tanımlanan Bitkiler:
                </Typography>
                {currentPlantContext.plants.slice(0, 3).map((plant, idx) => {
                  const sciName = plant.scientificName || plant.scientific_name || plant.name || 'Bilinmeyen';
                  const commonName = plant.commonName || plant.common_name || '';
                  const confidence = plant.confidence || plant.certainty || 0;
                  
                  // Güven skoruna göre renk
                  const getConfidenceColor = (conf) => {
                    if (conf >= 0.8) return 'success';
                    if (conf >= 0.6) return 'primary';
                    if (conf >= 0.4) return 'warning';
                    return 'default';
                  };
                  
                  return (
                    <Chip
                      key={idx}
                      label={`${idx + 1}. ${sciName}${commonName ? ` (${commonName})` : ''} - ${(confidence * 100).toFixed(0)}%`}
                      size="small"
                      sx={{ 
                        mr: 0.5, 
                        mb: 0.5,
                        fontWeight: idx === 0 ? 600 : 400
                      }}
                      color={getConfidenceColor(confidence)}
                      variant={idx === 0 ? "filled" : "outlined"}
                    />
                  );
                })}
                <Typography variant="caption" display="block" sx={{ mt: 1 }} color="text.secondary">
                  💡 Bu bitkiler hakkında soru sorabilirsiniz
                </Typography>
              </CardContent>
            </Card>
          )}
        </Grid>

        {/* Right Side - Chat Interface */}
        <Grid item xs={12} md={7}>
          <Paper
            elevation={3}
            sx={{
              height: 600,
              display: 'flex',
              flexDirection: 'column',
              overflow: 'hidden',
            }}
          >
            {/* Messages Area */}
            <List
              sx={{
                flex: 1,
                overflow: 'auto',
                p: 2,
                bgcolor: 'grey.50',
              }}
            >
              {messages.map((message, index) => (
                <ListItem
                  key={index}
                  sx={{
                    display: 'flex',
                    justifyContent: message.role === 'user' ? 'flex-end' : 'flex-start',
                    mb: 2,
                    px: 0,
                  }}
                >
                  <Box
                    sx={{
                      display: 'flex',
                      flexDirection: message.role === 'user' ? 'row-reverse' : 'row',
                      alignItems: 'flex-start',
                      maxWidth: '85%',
                    }}
                  >
                    <Avatar
                      sx={{
                        bgcolor: message.role === 'user' ? 'primary.main' : 'secondary.main',
                        mx: 1,
                      }}
                    >
                      {message.role === 'user' ? <PersonIcon /> : <SmartToyIcon />}
                    </Avatar>
                    
                    <Paper
                      elevation={1}
                      sx={{
                        p: 2,
                        bgcolor: message.role === 'user' ? 'primary.light' : 'white',
                        color: message.role === 'user' ? 'white' : 'text.primary',
                      }}
                    >
                      {message.hasImage && (
                        <Chip
                          icon={<ImageIcon />}
                          label={message.imageName}
                          size="small"
                          sx={{ mb: 1 }}
                        />
                      )}
                      
                      <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                        {message.content}
                      </Typography>

                      {message.confidence > 0 && (
                        <Chip
                          label={`Confidence: ${(message.confidence * 100).toFixed(1)}%`}
                          size="small"
                          color={message.confidence > 0.7 ? 'success' : 'warning'}
                          sx={{ mt: 1, mr: 0.5 }}
                        />
                      )}

                      {message.plants && message.plants.length > 0 && (
                        <Box sx={{ mt: 2, pt: 2, borderTop: '1px solid rgba(0,0,0,0.1)' }}>
                          <Typography variant="subtitle2" display="block" gutterBottom color="primary">
                            🌿 Tanımlanan Bitkiler ({message.total_matches || message.plants.length} eşleşme):
                          </Typography>
                          {message.plants.slice(0, 3).map((plant, idx) => {
                            const sciName = plant.scientificName || plant.scientific_name || plant.name || 'Bilinmeyen';
                            const commonName = plant.commonName || plant.common_name || '';
                            const confidence = plant.confidence || plant.certainty || 0;
                            const family = plant.family || '';
                            
                            const getConfidenceColor = (conf) => {
                              if (conf >= 0.8) return 'success';
                              if (conf >= 0.6) return 'primary';
                              if (conf >= 0.4) return 'warning';
                              return 'default';
                            };
                            
                            return (
                              <Box key={idx} sx={{ mb: 1 }}>
                                <Chip
                                  label={`${idx + 1}. ${sciName}`}
                                  size="small"
                                  color={getConfidenceColor(confidence)}
                                  variant={idx === 0 ? "filled" : "outlined"}
                                  sx={{ 
                                    mr: 0.5, 
                                    mb: 0.5,
                                    fontWeight: idx === 0 ? 600 : 400
                                  }}
                                />
                                {commonName && (
                                  <Chip
                                    label={commonName}
                                    size="small"
                                    sx={{ mr: 0.5, mb: 0.5 }}
                                    variant="outlined"
                                  />
                                )}
                                <Chip
                                  label={`${(confidence * 100).toFixed(0)}%`}
                                  size="small"
                                  color={getConfidenceColor(confidence)}
                                  sx={{ mr: 0.5, mb: 0.5 }}
                                />
                                {family && (
                                  <Typography variant="caption" display="block" sx={{ ml: 1, color: 'text.secondary' }}>
                                    Familya: {family}
                                  </Typography>
                                )}
                              </Box>
                            );
                          })}
                        </Box>
                      )}

                      <Typography variant="caption" display="block" sx={{ mt: 1, opacity: 0.7 }}>
                        {new Date(message.timestamp).toLocaleTimeString()}
                      </Typography>
                    </Paper>
                  </Box>
                </ListItem>
              ))}
              
              {loading && (
                <ListItem sx={{ justifyContent: 'flex-start' }}>
                  <CircularProgress size={24} />
                  <Typography variant="body2" sx={{ ml: 2 }}>
                    AI is thinking...
                  </Typography>
                </ListItem>
              )}
              
              <div ref={messagesEndRef} />
            </List>

            <Divider />

            {/* Input Area */}
            <Box sx={{ p: 2, bgcolor: 'background.paper' }}>
              {selectedImage && (
                <Alert severity="info" sx={{ mb: 1 }} icon={<ImageIcon />}>
                  Image attached: {selectedImage.name}
                  <IconButton size="small" onClick={handleRemoveImage} sx={{ ml: 1 }}>
                    <CloseIcon fontSize="small" />
                  </IconButton>
                </Alert>
              )}
              
              <Box sx={{ display: 'flex', gap: 1 }}>
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={(e) => {
                    const file = e.target.files[0];
                    if (file) handleFileSelect(file);
                  }}
                  accept="image/*"
                  style={{ display: 'none' }}
                />
                
                <IconButton
                  color="primary"
                  onClick={() => fileInputRef.current?.click()}
                  disabled={loading}
                >
                  <AttachFileIcon />
                </IconButton>
                
                <TextField
                  fullWidth
                  multiline
                  maxRows={4}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder={
                    selectedImage
                      ? 'Ask about this plant...'
                      : currentPlantContext
                      ? 'Ask follow-up questions...'
                      : 'Ask about plants or upload an image...'
                  }
                  disabled={loading}
                  variant="outlined"
                  size="small"
                />
                
                <IconButton
                  color="primary"
                  onClick={() => handleSend()}
                  disabled={loading || (!input.trim() && !selectedImage)}
                >
                  <SendIcon />
                </IconButton>
              </Box>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default InteractivePlantPage;
