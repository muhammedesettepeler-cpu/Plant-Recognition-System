import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Chip,
} from '@mui/material';

const getConfidenceColor = (conf) => {
  if (conf >= 0.8) return 'success';
  if (conf >= 0.6) return 'primary';
  if (conf >= 0.4) return 'warning';
  return 'default';
};

const PlantContextCard = ({ plantContext }) => {
  if (!plantContext) return null;

  return (
    <Card elevation={2} sx={{ mt: 2 }}>
      <CardContent>
        <Typography variant="subtitle2" gutterBottom color="primary">
          Tanımlanan Bitkiler:
        </Typography>
        {plantContext.plants.slice(0, 3).map((plant, idx) => {
          const sciName = plant.scientificName || plant.scientific_name || plant.name || 'Bilinmeyen';
          const commonName = plant.commonName || plant.common_name || '';
          const confidence = plant.confidence || plant.certainty || 0;
          
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
  );
};

export default PlantContextCard;
