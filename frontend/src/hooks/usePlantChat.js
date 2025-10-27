import { useState, useRef, useEffect } from 'react';
import { chatAPI, imageToFormData } from '../services/api';

// Generate a simple session ID
const generateSessionId = () => {
  return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
};

export const usePlantChat = () => {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: ' Hello! I\'m your botanical assistant. You can:\n\n• Upload a plant image to identify it\n• Ask questions about plants\n• Upload an image and ask specific questions about it\n\nHow can I help you today?',
      timestamp: new Date().toISOString(),
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId] = useState(() => generateSessionId());
  const [selectedImage, setSelectedImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [currentPlantContext, setCurrentPlantContext] = useState(null);
  
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleFileSelect = (file) => {
    setSelectedImage(file);
    setImagePreview(URL.createObjectURL(file));
  };

  const handleRemoveImage = () => {
    setSelectedImage(null);
    setImagePreview(null);
    setCurrentPlantContext(null);
  };

  const handleSend = async (customMessage = null) => {
    const messageText = customMessage || input;
    if (!messageText.trim() && !selectedImage) return;

    const userMessage = {
      role: 'user',
      content: messageText,
      timestamp: new Date().toISOString(),
      hasImage: !!selectedImage,
      imageName: selectedImage ? selectedImage.name : null,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      let response;

      if (selectedImage) {
        // Chat with image
        const formData = imageToFormData(selectedImage, {
          message: messageText || 'Please identify this plant and provide information about it.',
          session_id: sessionId,
        });

        response = await chatAPI.sendImageMessage(formData);
        
        // Save plant context for follow-up questions
        if (response.data.identified_plants && response.data.identified_plants.length > 0) {
          setCurrentPlantContext({
            plants: response.data.identified_plants,
            image: imagePreview,
            timestamp: response.data.timestamp,
          });
        }
      } else {
        // Text-only chat (might reference previous plant context)
        let contextMessage = messageText;
        if (currentPlantContext) {
          const plantNames = currentPlantContext.plants
            .map(p => p.scientificName || p.scientific_name)
            .join(', ');
          contextMessage = `Regarding the previously identified plants (${plantNames}): ${messageText}`;
        }

        response = await chatAPI.sendMessage({
          message: contextMessage,
          session_id: sessionId,
          conversation_history: messages
            .filter((m) => !m.error)
            .map(({ role, content }) => ({ role, content })),
        });
      }

      // Debug: Backend'den gelen response'u kontrol et
      console.log('Backend response:', response.data);
      
      const assistantMessage = {
        role: 'assistant',
        content: response.data.response,
        timestamp: response.data.timestamp,
        plants: response.data.identified_plants || response.data.relevant_plants || [],
        confidence: response.data.highest_confidence || response.data.confidence || 0,
        total_matches: response.data.total_matches,
        similarity_results: response.data.similarity_results,
      };
      
      console.log('Assistant message confidence:', assistantMessage.confidence);

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage = {
        role: 'assistant',
        content: error.message || 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString(),
        error: true,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickIdentify = async () => {
    if (!selectedImage) return;
    await handleSend('Please identify this plant and provide detailed information about it.');
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return {
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
  };
};
