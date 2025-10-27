import httpx
from typing import Optional
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class LLMService:
    """Google Gemini AI servisi (OpenRouter yerine)"""
    def __init__(self):
        # Tercih: Google AI Studio, yoksa OpenRouter
        self.google_api_key = settings.GOOGLE_AI_STUDIO_API_KEY
        self.google_model = settings.GOOGLE_AI_STUDIO_MODEL

        self.api_key = settings.OPENROUTER_API_KEY
        self.api_url = settings.OPENROUTER_BASE_URL
        self.model = settings.OPENROUTER_MODEL

        # Google Gemini client (lazy init)
        self._google_client = None

        # Default headers for OpenRouter (kept for fallback)
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "Plant Recognition System"
        }

    @property
    def google_client(self):
        """Lazy initialization of Google Gemini client"""
        if self._google_client is None and self.google_api_key:
            try:
                from google import genai
                self._google_client = genai.Client(api_key=self.google_api_key)
                logger.info("✅ Google Gemini client initialized")
            except ImportError:
                logger.warning("google-genai package not installed, falling back to OpenRouter")
            except Exception as e:
                logger.error(f"Failed to initialize Google Gemini client: {e}")
        return self._google_client
    
    async def generate_response(self, prompt: str, context: Optional[str] = None) -> str:
        try:
            system_prompt = """Sen uzman bir botanik asistanısın. Türkçe olarak yanıt ver.

KURALLAR:
1. SADECE Türkçe yanıt ver - başka dil kullanma
2. Net, anlaşılır ve bilimsel doğru bilgi ver
3. Bitki adlarını format: "Bilimsel Ad (Türkçe İsim)" şeklinde yaz
4. Güven skorlarını belirt
5. Kısa ve öz bilgi ver (2-3 paragraf)
6. Abartma, sadece verilen context bilgisini kullan

YASAKLAR:
- Karma dil kullanımı (Korece, Japonca, İngilizce, Rusça karışık)
- Anlamsız kelimeler
- Uydurma bilgi
- Çok uzun açıklamalar"""
            
            if context:
                system_prompt += f"\n\nVERİTABANI BİLGİSİ:\n{context}"
            
            # Compose full prompt
            full_prompt = system_prompt + "\n\nKullanıcı Sorusu:\n" + prompt

            # If Google AI Studio key is provided, use it (preferred)
            if self.google_client:
                logger.info(f" Using Google Gemini: {self.google_model}")
                try:
                    response = self.google_client.models.generate_content(
                        model=self.google_model,
                        contents=full_prompt
                    )
                    
                    # Extract text from response
                    if hasattr(response, 'text'):
                        logger.info(" Google Gemini response received")
                        return response.text
                    elif hasattr(response, 'candidates') and len(response.candidates) > 0:
                        candidate = response.candidates[0]
                        if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                            text = ''.join(part.text for part in candidate.content.parts if hasattr(part, 'text'))
                            logger.info(" Google Gemini response received (from candidates)")
                            return text
                    
                    logger.warning(" Google Gemini returned unexpected format, falling back to OpenRouter")
                except Exception as e:
                    logger.error(f" Google Gemini API error: {e}, falling back to OpenRouter")

            # Otherwise fallback to OpenRouter
            logger.info(f" Using OpenRouter (fallback): {self.model}")
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
            
            payload = {
                "model": self.model,
                "messages": messages,
                "max_tokens": 400,
                "temperature": 0.3,  # Daha tutarlı yanıtlar için düşük temperature
                "top_p": 0.9,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.api_url}/chat/completions",
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                result = response.json()
                return result["choices"][0]["message"]["content"]
        except httpx.HTTPStatusError as e:
            error_detail = e.response.text if hasattr(e, 'response') else str(e)
            logger.error(f"OpenRouter API HTTP error: {e.response.status_code} - {error_detail}")
            
            # 429 Rate Limit veya diğer hatalar için fallback
            if e.response.status_code == 429:
                logger.warning("Rate limit hit, using fallback response")
            
            # Hata durumunda basit fallback (bitki verisi olmadan)
            raise  # Hata fırlat ki generate_rag_response fallback'i çağırsın
        except httpx.TimeoutException:
            logger.error("OpenRouter API timeout")
            raise  # Hata fırlat ki generate_rag_response fallback'i çağırsın
        except KeyError as e:
            logger.error(f"Unexpected API response format: {e}")
            raise  # Hata fırlat ki generate_rag_response fallback'i çağırsın
        except Exception as e:
            logger.error(f"LLM service error: {type(e).__name__} - {str(e)}")
            raise  # Hata fırlat ki generate_rag_response fallback'i çağırsın
    
    def _generate_fallback_response(self, prompt: str, plants: list = None) -> str:
        """LLM kullanılamadığında bitki bilgileriyle zengin yanıt üret"""
        logger.info(f"Using fallback response with {len(plants) if plants else 0} plants")
        
        # Eğer bitki verisi varsa, detaylı bilgi ver
        if plants and len(plants) > 0:
            response_parts = ["Görsel analizi tamamlandı! İşte bulunan olası bitkiler:\n"]
            
            for idx, plant in enumerate(plants[:3], 1):
                sci_name = plant.get('scientificName', 'Bilinmeyen')
                common_name = plant.get('commonName', '')
                
                # Weaviate'den gelen certainty değeri _additional nesnesinde
                additional = plant.get('_additional', {})
                confidence = additional.get('certainty', plant.get('certainty', plant.get('score', 0)))
                
                # Eğer hala 0 ise distance'dan hesapla
                if confidence == 0 and 'distance' in additional:
                    distance = additional.get('distance', 2)
                    confidence = max(0.0, min(1.0, 1 - (distance / 2)))
                
                family = plant.get('family', '')
                
                response_parts.append(f"\n{idx}. **{sci_name}**")
                if common_name:
                    response_parts.append(f" ({common_name})")
                response_parts.append(f"\n   - Güven skoru: {confidence:.1%}")
                if family:
                    response_parts.append(f"\n   - Familya: {family}")
                
                logger.debug(f"Fallback plant {idx}: {sci_name} - {confidence:.1%}")
            
            response_parts.append("\n\n Bu bitkilerden biri hakkında daha fazla bilgi almak için soru sorabilirsiniz.")
            return "".join(response_parts)
        
        # Bitki verisi yoksa genel yanıt
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ['identify', 'what', 'which', 'plant', 'species']):
            return ("Görsel analizi yapıldı ancak veritabanında eşleşme bulunamadı. "
                   "Lütfen daha net bir fotoğraf deneyin veya farklı açıdan çekilmiş bir görsel yükleyin.")
        
        if any(word in prompt_lower for word in ['care', 'water', 'sun', 'grow', 'bakım']):
            return ("Genel bitki bakım önerileri:\n"
                   "-  Düzenli sulama (toprağın nemini kontrol edin)\n"
                   "-  Yeterli güneş ışığı (bitkiye göre değişir)\n"
                   "-  İyi drene olan toprak kullanın\n"
                   "-  Uygun sıcaklık (15-25°C ideal)\n\n"
                   "Daha spesifik bilgi için bitkinin adını belirtin.")
        
        return ("İsteğiniz işlendi. Lütfen aşağıdaki sonuçları kontrol edin veya "
               "birkaç dakika sonra tekrar deneyin.")
    
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
        
        try:
            return await self.generate_response(user_query, context)
        except Exception as e:
            # LLM başarısız olursa, bitki bilgileriyle fallback yanıt üret
            logger.warning(f"LLM failed, using fallback with plant data: {e}")
            return self._generate_fallback_response(user_query, retrieved_plants)

# Global instance (geriye dönük uyumluluk için)
llm_service = LLMService()
grok_service = llm_service  # Eski kod ile uyumluluk

