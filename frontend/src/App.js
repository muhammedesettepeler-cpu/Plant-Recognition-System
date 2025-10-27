import React, { useState, useEffect } from 'react';
import { Routes, Route } from 'react-router-dom';
import { Container, AppBar, Toolbar, Typography, Box, Alert, Snackbar } from '@mui/material';
import HomePage from './pages/HomePage';
import InteractivePlantPage from './pages/InteractivePlantPage';
import Navigation from './components/Navigation';
import { healthAPI } from './services/api';

function App() {
  const [backendStatus, setBackendStatus] = useState({ online: null, message: '' });
  const [showAlert, setShowAlert] = useState(false);

  useEffect(() => {
    // Check backend health on startup
    const checkHealth = async () => {
      try {
        const response = await healthAPI.getHealth();
        setBackendStatus({
          online: true,
          message: `Backend is online - ${response.data.status}`,
        });
      } catch (error) {
        setBackendStatus({
          online: false,
          message: 'Backend is offline. Please start the backend server.',
        });
        setShowAlert(true);
      }
    };

    checkHealth();
  }, []);

  return (
    <Box 
      sx={{ 
        display: 'flex', 
        flexDirection: 'column', 
        minHeight: '100vh',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {/* Animated Background */}
      <Box
        sx={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          zIndex: -1,
          background: `
            radial-gradient(ellipse at 20% 30%, rgba(147, 51, 234, 0.15) 0%, transparent 50%),
            radial-gradient(ellipse at 80% 70%, rgba(45, 106, 79, 0.2) 0%, transparent 50%),
            radial-gradient(ellipse at 50% 50%, rgba(82, 183, 136, 0.1) 0%, transparent 50%),
            linear-gradient(135deg, #f8f9fa 0%, #ffffff 50%, #f0f4f8 100%)
          `,
          '&::before': {
            content: '""',
            position: 'absolute',
            top: '-50%',
            left: '-50%',
            width: '200%',
            height: '200%',
            background: `
              radial-gradient(circle at 30% 40%, rgba(147, 51, 234, 0.08) 0%, transparent 25%),
              radial-gradient(circle at 70% 60%, rgba(45, 106, 79, 0.12) 0%, transparent 25%)
            `,
            animation: 'float 20s ease-in-out infinite',
          },
          '@keyframes float': {
            '0%, 100%': {
              transform: 'translate(0, 0) rotate(0deg)',
            },
            '33%': {
              transform: 'translate(30px, -30px) rotate(120deg)',
            },
            '66%': {
              transform: 'translate(-20px, 20px) rotate(240deg)',
            },
          },
        }}
      />
      
      {/* Health Status Alert */}
      <Snackbar
        open={showAlert && backendStatus.online === false}
        autoHideDuration={10000}
        onClose={() => setShowAlert(false)}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <Alert
          onClose={() => setShowAlert(false)}
          severity="error"
          sx={{ width: '100%' }}
        >
          {backendStatus.message}
        </Alert>
      </Snackbar>

      <AppBar 
        position="fixed" 
        elevation={0}
        sx={{ 
          top: 0,
          left: 0,
          right: 0,
          zIndex: (theme) => theme.zIndex.appBar + 10,
          background: 'rgba(255, 255, 255, 0.95)',
          backdropFilter: 'blur(10px)',
          borderBottom: '1px solid rgba(0,0,0,0.08)',
        }}
      >
        <Toolbar sx={{ py: 1, minHeight: 72 }}>
          <Box
            onClick={() => window.location.href = '/'}
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 2,
              flexGrow: 0,
              mr: 'auto',
              cursor: 'pointer',
              '&:hover': {
                opacity: 0.8,
              },
              transition: 'opacity 0.2s ease',
            }}
          >
            <Box
              component="img"
              src="/logo.jpg"
              alt="Bitki Tanı Logo"
              sx={{
                height: 56,
                width: 56,
                borderRadius: '16px',
                boxShadow: '0 4px 12px rgba(45, 106, 79, 0.2)',
                transition: 'all 0.3s ease',
                '&:hover': {
                  transform: 'scale(1.05)',
                  boxShadow: '0 6px 16px rgba(45, 106, 79, 0.3)',
                },
              }}
            />
            <Box>
              <Typography
                variant="h5"
                component="div"
                sx={{
                  fontWeight: 800,
                  background: 'linear-gradient(135deg, #2d6a4f 0%, #52b788 100%)',
                  backgroundClip: 'text',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  letterSpacing: '-0.02em',
                }}
              >
                Bitki Tanı
              </Typography>
              <Typography
                variant="caption"
                sx={{
                  color: 'text.secondary',
                  fontWeight: 500,
                  letterSpacing: '0.05em',
                  fontSize: '0.7rem',
                }}
              >
                AI-POWERED RECOGNITION
              </Typography>
            </Box>
          </Box>
          <Navigation />
        </Toolbar>
      </AppBar>

  {/* Add top padding so fixed AppBar doesn't overlap content (equal to toolbar height) */}
  <Container maxWidth="xl" sx={{ pt: '88px', mt: 0, mb: 4, flex: 1 }}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/assistant" element={<InteractivePlantPage />} />
          {/* Legacy routes redirect to new page */}
          <Route path="/recognize" element={<InteractivePlantPage />} />
          <Route path="/chat" element={<InteractivePlantPage />} />
        </Routes>
      </Container>

      <Box
        component="footer"
        sx={{
          py: 4,
          px: 2,
          mt: 'auto',
          background: 'linear-gradient(135deg, rgba(45, 106, 79, 0.03) 0%, rgba(82, 183, 136, 0.03) 100%)',
          borderTop: '1px solid rgba(0,0,0,0.06)',
        }}
      >
        <Container maxWidth="lg">
          <Typography 
            variant="body2" 
            align="center"
            sx={{ 
              color: 'text.secondary',
              fontWeight: 500,
            }}
          >
            © 2025 Bitki Tanı - AI-Powered Botanical Assistant
          </Typography>
          <Typography 
            variant="caption" 
            align="center"
            display="block"
            sx={{ 
              color: 'text.secondary',
              mt: 0.5,
              opacity: 0.7,
            }}
          >
            Powered by CLIP, Weaviate & OpenRouter
          </Typography>
        </Container>
      </Box>
    </Box>
  );
}

export default App;
