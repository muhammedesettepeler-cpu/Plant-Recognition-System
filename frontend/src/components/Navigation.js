import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button, Box } from '@mui/material';
import HomeIcon from '@mui/icons-material/Home';
import PhotoCameraIcon from '@mui/icons-material/PhotoCamera';
import ChatIcon from '@mui/icons-material/Chat';

const Navigation = () => {
  const navigate = useNavigate();

  return (
    <Box sx={{ display: 'flex', gap: 2 }}>
      <Button
        color="inherit"
        startIcon={<HomeIcon />}
        onClick={() => navigate('/')}
      >
        Home
      </Button>
      <Button
        color="inherit"
        startIcon={<PhotoCameraIcon />}
        onClick={() => navigate('/recognize')}
      >
        Recognize
      </Button>
      <Button
        color="inherit"
        startIcon={<ChatIcon />}
        onClick={() => navigate('/chat')}
      >
        Chat
      </Button>
    </Box>
  );
};

export default Navigation;
