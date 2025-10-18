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
import NatureIcon from '@mui/icons-material/Nature';

const HomePage = () => {
  const navigate = useNavigate();

  return (
    <Container maxWidth="lg">
      <Box sx={{ textAlign: 'center', mb: 6 }}>
        <NatureIcon sx={{ fontSize: 80, color: 'primary.main', mb: 2 }} />
        <Typography variant="h2" component="h1" gutterBottom>
          Welcome to Plant Recognition System
        </Typography>
        <Typography variant="h5" color="text.secondary" paragraph>
          AI-Powered Botanical Assistant
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ maxWidth: 800, mx: 'auto' }}>
          Identify plants instantly using advanced AI technology. Upload a photo or describe
          a plant to get detailed information about species, care instructions, and more.
        </Typography>
      </Box>

      <Grid container spacing={4}>
        <Grid item xs={12} md={6}>
          <Card elevation={3} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <CardContent sx={{ flexGrow: 1 }}>
              <PhotoCameraIcon sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
              <Typography variant="h5" component="h2" gutterBottom>
                Image Recognition
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Upload a plant image and let our AI identify it for you. Get instant results
                with detailed information about the plant species, characteristics, and care
                instructions.
              </Typography>
            </CardContent>
            <CardActions>
              <Button
                size="large"
                variant="contained"
                fullWidth
                onClick={() => navigate('/recognize')}
              >
                Start Recognition
              </Button>
            </CardActions>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card elevation={3} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <CardContent sx={{ flexGrow: 1 }}>
              <ChatIcon sx={{ fontSize: 60, color: 'secondary.main', mb: 2 }} />
              <Typography variant="h5" component="h2" gutterBottom>
                Chatbot Assistant
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Have questions about plants? Chat with our AI-powered botanical assistant.
                Ask about plant care, identification, habitat, and much more in natural language.
              </Typography>
            </CardContent>
            <CardActions>
              <Button
                size="large"
                variant="contained"
                color="secondary"
                fullWidth
                onClick={() => navigate('/chat')}
              >
                Start Chatting
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
