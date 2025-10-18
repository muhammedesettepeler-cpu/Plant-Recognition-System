import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Container,
} from '@mui/material';
import PhotoCameraIcon from '@mui/icons-material/PhotoCamera';
import ChatIcon from '@mui/icons-material/Chat';

const HomePage = () => {
  const navigate = useNavigate();

  return (
    <Container maxWidth="lg">
      <Box sx={{ textAlign: 'center', mb: 8, mt: 4 }}>
        <Box
          sx={{
            display: 'inline-block',
            mb: 3,
          }}
        >
          <Box
            component="img"
            src="/logo.jpg"
            alt="Bitki Tanı Logo"
            sx={{
              height: 120,
              width: 120,
              borderRadius: '32px',
              boxShadow: '0 12px 40px rgba(45, 106, 79, 0.3)',
              transition: 'all 0.4s ease',
              '&:hover': {
                transform: 'scale(1.1) rotate(5deg)',
                boxShadow: '0 16px 50px rgba(45, 106, 79, 0.4)',
              },
            }}
          />
        </Box>
        <Typography 
          variant="h2" 
          component="h1" 
          gutterBottom
          sx={{
            fontWeight: 800,
            background: 'linear-gradient(135deg, #2d6a4f 0%, #52b788 100%)',
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            mb: 2,
          }}
        >
          Welcome to Bitki Tanı
        </Typography>
        <Typography 
          variant="h5" 
          sx={{ 
            color: 'text.secondary',
            fontWeight: 500,
            mb: 3,
          }}
        >
          Your AI-Powered Botanical Assistant
        </Typography>
        <Typography 
          variant="body1" 
          sx={{ 
            color: 'text.secondary',
            maxWidth: 700,
            mx: 'auto',
            fontSize: '1.1rem',
            lineHeight: 1.7,
          }}
        >
          Identify plants instantly using advanced AI technology. Upload a photo or ask
          questions to get detailed information about species, care instructions, and more.
        </Typography>
      </Box>

      <Grid container spacing={4} justifyContent="center">
        <Grid item xs={12} md={9}>
          <Card 
            elevation={0}
            sx={{ 
              height: '100%',
              background: 'linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(248,249,250,0.9) 100%)',
              border: '1px solid rgba(45, 106, 79, 0.1)',
              overflow: 'hidden',
              position: 'relative',
            }}
          >
            <Box
              sx={{
                position: 'absolute',
                top: -50,
                right: -50,
                width: 200,
                height: 200,
                borderRadius: '50%',
                background: 'radial-gradient(circle, rgba(82, 183, 136, 0.15) 0%, transparent 70%)',
              }}
            />
            <CardContent sx={{ p: 4, position: 'relative', zIndex: 1 }}>
              <Box sx={{ display: 'flex', justifyContent: 'center', gap: 3, mb: 3 }}>
                <Box
                  sx={{
                    p: 2,
                    borderRadius: '16px',
                    background: 'linear-gradient(135deg, rgba(45, 106, 79, 0.1) 0%, rgba(82, 183, 136, 0.1) 100%)',
                  }}
                >
                  <PhotoCameraIcon sx={{ fontSize: 48, color: 'primary.main' }} />
                </Box>
                <Box
                  sx={{
                    p: 2,
                    borderRadius: '16px',
                    background: 'linear-gradient(135deg, rgba(244, 162, 97, 0.1) 0%, rgba(246, 189, 96, 0.1) 100%)',
                  }}
                >
                  <ChatIcon sx={{ fontSize: 48, color: 'secondary.main' }} />
                </Box>
              </Box>
              
              <Typography 
                variant="h4" 
                component="h2" 
                gutterBottom 
                align="center"
                sx={{ fontWeight: 700, mb: 3 }}
              >
                Interactive Plant Assistant
              </Typography>
              
              <Typography 
                variant="body1" 
                sx={{ 
                  color: 'text.secondary',
                  mb: 4,
                  fontSize: '1.1rem',
                  lineHeight: 1.7,
                  textAlign: 'center',
                }}
              >
                Experience our unified plant assistant that combines the power of image recognition
                and conversational AI in one seamless interface.
              </Typography>

              <Grid container spacing={2} sx={{ mb: 4 }}>
                {[
                  { icon: '📸', title: 'Upload Images', desc: 'Instant AI-powered identification' },
                  { icon: '💬', title: 'Chat with AI', desc: 'Ask questions about any plant' },
                  { icon: '🔍', title: 'Follow-up', desc: 'Context-aware conversations' },
                  { icon: '🌿', title: 'Smart Analysis', desc: 'Detailed botanical insights' },
                  { icon: '⚡', title: 'Fast Results', desc: 'Powered by CLIP & Weaviate' },
                  { icon: '🎯', title: 'Accurate', desc: '10,000+ plant species' },
                ].map((feature, idx) => (
                  <Grid item xs={12} sm={6} md={4} key={idx}>
                    <Box
                      sx={{
                        p: 2,
                        borderRadius: 2,
                        background: 'white',
                        border: '1px solid rgba(0,0,0,0.06)',
                        transition: 'all 0.2s ease',
                        '&:hover': {
                          transform: 'translateY(-4px)',
                          boxShadow: '0 8px 24px rgba(0,0,0,0.08)',
                          borderColor: 'primary.main',
                        },
                      }}
                    >
                      <Typography variant="h4" sx={{ mb: 0.5 }}>{feature.icon}</Typography>
                      <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 0.5 }}>
                        {feature.title}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {feature.desc}
                      </Typography>
                    </Box>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
            
            <CardActions sx={{ p: 4, pt: 0 }}>
              <Button
                size="large"
                variant="contained"
                fullWidth
                onClick={() => navigate('/assistant')}
                sx={{ 
                  py: 2,
                  fontSize: '1.1rem',
                  fontWeight: 700,
                  background: 'linear-gradient(135deg, #2d6a4f 0%, #52b788 100%)',
                  boxShadow: '0 8px 24px rgba(45, 106, 79, 0.3)',
                  '&:hover': {
                    background: 'linear-gradient(135deg, #1b4332 0%, #2d6a4f 100%)',
                    boxShadow: '0 12px 32px rgba(45, 106, 79, 0.4)',
                    transform: 'translateY(-2px)',
                  },
                  transition: 'all 0.3s ease',
                }}
              >
                Launch Plant Assistant →
              </Button>
            </CardActions>
          </Card>
        </Grid>
      </Grid>

      <Box sx={{ mt: 6, textAlign: 'center' }}>
        <Typography variant="h5" gutterBottom>
          Features
        </Typography>
        <Grid container spacing={3} sx={{ mt: 2 }}>
          <Grid item xs={12} sm={4}>
            <Typography variant="h6" color="primary">
              PlantNet Integration
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Powered by PlantNet's extensive database
            </Typography>
          </Grid>
          <Grid item xs={12} sm={4}>
            <Typography variant="h6" color="primary">
              CLIP Embeddings
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Advanced visual understanding with CLIP
            </Typography>
          </Grid>
          <Grid item xs={12} sm={4}>
            <Typography variant="h6" color="primary">
              LLM Responses
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Natural language explanations via Grok
            </Typography>
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
};

export default HomePage;
