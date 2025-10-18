import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Container, AppBar, Toolbar, Typography, Box } from '@mui/material';
import NatureIcon from '@mui/icons-material/Nature';
import HomePage from './pages/HomePage';
import RecognitionPage from './pages/RecognitionPage';
import ChatbotPage from './pages/ChatbotPage';
import Navigation from './components/Navigation';

function App() {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <AppBar position="static" elevation={2}>
        <Toolbar>
          <NatureIcon sx={{ mr: 2, fontSize: 32 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Plant Recognition System
          </Typography>
          <Navigation />
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ mt: 4, mb: 4, flex: 1 }}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/recognize" element={<RecognitionPage />} />
          <Route path="/chat" element={<ChatbotPage />} />
        </Routes>
      </Container>

      <Box
        component="footer"
        sx={{
          py: 3,
          px: 2,
          mt: 'auto',
          backgroundColor: (theme) => theme.palette.grey[200],
        }}
      >
        <Container maxWidth="lg">
          <Typography variant="body2" color="text.secondary" align="center">
            © 2025 Plant Recognition System - AI-Powered Botanical Assistant
          </Typography>
        </Container>
      </Box>
    </Box>
  );
}

export default App;
