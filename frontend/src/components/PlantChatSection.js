import React, { useRef } from 'react';
import {
  Box,
  Paper,
  TextField,
  IconButton,
  Divider,
  CircularProgress,
  Typography,
  List,
  ListItem,
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import AttachFileIcon from '@mui/icons-material/AttachFile';
import PlantMessageItem from './PlantMessageItem';

const PlantChatSection = ({
  messages,
  input,
  setInput,
  loading,
  selectedImage,
  currentPlantContext,
  messagesEndRef,
  onSend,
  onKeyPress,
  onFileSelect,
  onRemoveImage,
}) => {
  const fileInputRef = useRef(null);

  return (
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
          <PlantMessageItem key={index} message={message} />
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
        {/* Image attachment notification removed for cleaner UI */}
        
        <Box sx={{ display: 'flex', gap: 1 }}>
          <input
            type="file"
            ref={fileInputRef}
            onChange={(e) => {
              const file = e.target.files[0];
              if (file) onFileSelect(file);
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
            onKeyPress={onKeyPress}
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
            onClick={() => onSend()}
            disabled={loading || (!input.trim() && !selectedImage)}
          >
            <SendIcon />
          </IconButton>
        </Box>
      </Box>
    </Paper>
  );
};

export default PlantChatSection;
