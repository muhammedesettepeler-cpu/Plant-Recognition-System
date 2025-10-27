import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Chip,
  Avatar,
  ListItem,
} from '@mui/material';
import PersonIcon from '@mui/icons-material/Person';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import ImageIcon from '@mui/icons-material/Image';

const getConfidenceColor = (conf) => {
  if (conf >= 0.8) return 'success';
  if (conf >= 0.6) return 'primary';
  if (conf >= 0.4) return 'warning';
  return 'default';
};

const PlantMessageItem = ({ message }) => {
  return (
    <ListItem
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

          {/* Sadece confidence varsa ve 0'dan büyükse göster */}
          {message.confidence && message.confidence > 0 && (
            <Chip
              label={`Overall Confidence: ${(message.confidence * 100).toFixed(1)}%`}
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
  );
};

export default PlantMessageItem;
