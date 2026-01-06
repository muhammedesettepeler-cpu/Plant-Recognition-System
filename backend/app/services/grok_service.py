"""
LLM Service - Simple template-based response generator
Uses plant data from recognition APIs without external LLM
"""

import logging
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)


class LLMService:
    """Template-based plant response generator"""

    def __init__(self):
        logger.info("✅ Template-based response generator initialized")

    async def generate_response(
        self, prompt: str, context: Optional[str] = None
    ) -> str:
        """Generate response using templates and context"""
        return self._generate_plant_response(prompt, context)

    def _generate_plant_response(
        self, prompt: str, context: Optional[str] = None
    ) -> str:
        """Generate formatted plant response from context"""
        if not context:
            return "Bitki analizi yapıldı ancak eşleşen sonuç bulunamadı. Lütfen daha net bir görsel ile tekrar deneyin."

        # Parse context to extract plant info
        response_parts = ["🌿 **Görsel Analizi Tamamlandı!**\n"]

        # Add context directly - it's already formatted
        response_parts.append("**Bulunan Bitkiler:**")
        response_parts.append(context)
        response_parts.append("")

        # Add helpful info based on query type
        query_lower = prompt.lower()

        if any(word in query_lower for word in ["bakım", "sulama", "yetiştir", "care"]):
            response_parts.append("**💡 Bakım Önerileri:**")
            response_parts.append("- Bitkinin türüne göre sulama ihtiyacı değişir")
            response_parts.append("- Dolaylı güneş ışığı çoğu bitki için idealdir")
            response_parts.append("- Toprağın üst kısmı kuruduğunda sulayın")

        elif any(
            word in query_lower for word in ["zehir", "tehlike", "toxic", "poison"]
        ):
            response_parts.append("**⚠️ Uyarı:**")
            response_parts.append(
                "- Bazı bitkiler evcil hayvanlar için zararlı olabilir"
            )
            response_parts.append("- Detaylı bilgi için uzman görüşü alın")

        else:
            response_parts.append("**📝 Not:**")
            response_parts.append(
                "- Yukarıdaki bilgiler Kaggle PlantCLEF, PlantNet ve USDA veritabanlarından alınmıştır"
            )
            response_parts.append("- Kesin tanımlama için uzman görüşü önerilir")

        return "\n".join(response_parts)

    async def generate_rag_response(
        self, query: str, context: str, plants: list = None
    ) -> str:
        """RAG response with plant context"""
        return await self.generate_response(query, context)


# Global instance
grok_service = LLMService()
