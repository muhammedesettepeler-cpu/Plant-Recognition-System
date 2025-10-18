import httpx
from typing import Optional
from app.core.config import settings

class LLMService:
    """OpenRouter LLM servisi (Grok yerine ücretsiz ve güçlü!)"""
    def __init__(self):
        # OpenRouter kullan (ücretsiz ve daha iyi!)
        self.api_key = settings.OPENROUTER_API_KEY
        self.api_url = settings.OPENROUTER_BASE_URL
        self.model = settings.OPENROUTER_MODEL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "Plant Recognition System"
        }
    
    async def generate_response(self, prompt: str, context: Optional[str] = None) -> str:
        try:
            system_prompt = "You are an expert botanist assistant. Provide accurate, helpful information about plants."
            if context:
                system_prompt += f"\n\nContext: {context}"
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
            
            payload = {
                "model": self.model,
                "messages": messages,
                "max_tokens": 500,
                "temperature": 0.7
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.api_url}/chat/completions",
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"LLM error: {e}")
            return "Sorry, I'm having trouble responding right now. Please try again."
    
    async def generate_rag_response(self, user_query: str, retrieved_plants: list) -> str:
        """RAG: Veritabanından alınan bitki bilgileriyle zenginleştirilmiş yanıt"""
        plant_context = []
        for plant in retrieved_plants[:3]:
            plant_info = f"- {plant.get('scientificName', 'Unknown')}"
            if plant.get('commonName'):
                plant_info += f" ({plant.get('commonName')})"
            if plant.get('family'):
                plant_info += f" - Family: {plant.get('family')}"
            plant_context.append(plant_info)
        
        context = "Relevant plants from database:\n" + "\n".join(plant_context) if plant_context else None
        return await self.generate_response(user_query, context)

# Global instance (geriye dönük uyumluluk için)
llm_service = LLMService()
grok_service = llm_service  # Eski kod ile uyumluluk

