import React from 'react';
import {
  Box,
  Typography,
  Grid,
} from '@mui/material';
import { usePlantChat } from '../hooks/usePlantChat';
import PlantImageUploadSection from '../components/PlantImageUploadSection';
import PlantContextCard from '../components/PlantContextCard';
import PlantChatSection from '../components/PlantChatSection';

const InteractivePlantPage = () => {
  const {
    // State
    messages,
    input,
    setInput,
    loading,
    selectedImage,
    imagePreview,
    currentPlantContext,
    messagesEndRef,
    
    // Handlers
    handleFileSelect,
    handleRemoveImage,
    handleSend,
    handleQuickIdentify,
    handleKeyPress,
  } = usePlantChat();

  return (
    <Box sx={{ position: 'relative', minHeight: 'calc(100vh - 200px)' }}>
      {/* Background gradient */}
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
      
      {/* Header */}
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
        <Grid item xs={12} md={4}>
          <PlantImageUploadSection
            imagePreview={imagePreview}
            selectedImage={selectedImage}
            loading={loading}
            onFileSelect={handleFileSelect}
            onRemoveImage={handleRemoveImage}
            onQuickIdentify={handleQuickIdentify}
          />
          
          <PlantContextCard plantContext={currentPlantContext} />
        </Grid>

        {/* Right Side - Chat Interface */}
        <Grid item xs={12} md={8}>
          <PlantChatSection
            messages={messages}
            input={input}
            setInput={setInput}
            loading={loading}
            selectedImage={selectedImage}
            currentPlantContext={currentPlantContext}
            messagesEndRef={messagesEndRef}
            onSend={handleSend}
            onKeyPress={handleKeyPress}
            onFileSelect={handleFileSelect}
            onRemoveImage={handleRemoveImage}
          />
        </Grid>
      </Grid>
    </Box>
  );
};

export default InteractivePlantPage;
