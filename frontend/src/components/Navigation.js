import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Button, Box } from '@mui/material';
import HomeIcon from '@mui/icons-material/Home';
import NaturePeopleIcon from '@mui/icons-material/NaturePeople';

const Navigation = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'Home', icon: <HomeIcon /> },
    { path: '/assistant', label: 'Plant Assistant', icon: <NaturePeopleIcon /> },
  ];

  return (
    <Box sx={{ display: 'flex', gap: 1.5 }}>
      {navItems.map((item) => {
        const isActive = location.pathname === item.path || 
                        (item.path === '/assistant' && ['/recognize', '/chat'].includes(location.pathname));
        
        return (
          <Button
            key={item.path}
            startIcon={item.icon}
            onClick={() => navigate(item.path)}
            sx={{
              color: isActive ? 'primary.main' : 'text.primary',
              fontWeight: isActive ? 700 : 500,
              px: { xs: 1.5, sm: 2.5 },
              py: { xs: 0.5, sm: 1 },
              borderRadius: 2,
              backgroundColor: isActive ? 'rgba(45, 106, 79, 0.08)' : 'transparent',
              '&:hover': {
                backgroundColor: isActive ? 'rgba(45, 106, 79, 0.12)' : 'rgba(0, 0, 0, 0.04)',
              },
              transition: 'all 0.2s ease',
            }}
          >
            {item.label}
          </Button>
        );
      })}
    </Box>
  );
};

export default Navigation;
