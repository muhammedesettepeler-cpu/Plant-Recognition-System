"""
Seed PostgreSQL with detailed plant data
Populates plants table with Rosa and Tulipa species information
"""
import sys
sys.path.insert(0, 'backend')

from app.db.base import SessionLocal
from app.services.plant_repository import plant_repository
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Detaylı bitki bilgileri - Rosa ve Tulipa türleri
SEED_PLANTS = [
    {
        "scientific_name": "Rosa gallica",
        "scientific_name_full": "Rosa gallica L.",
        "common_names": ["French Rose", "Fransız Gülü", "Galya Gülü"],
        "family": "Rosaceae",
        "genus": "Rosa",
        "description": "Avrupa'nın güney ve orta bölgelerine özgü bir gül türüdür. Koyu pembe ila kırmızı renkte çiçekleriyle bilinir. Yüksekliği 60-120 cm arasında değişir ve geç ilkbahar ile erken yaz aylarında çiçek açar.",
        "habitat": "İyi drene olmuş, hafif asidik ila nötr pH'lı topraklarda yetişir. Tam güneş ışığı veya yarı gölge alanları tercih eder.",
        "care_instructions": "💧 Sulama: Düzenli ama aşırı olmayan sulama. Toprağın nemini kontrol edin.\n☀️ Işık: Tam güneş ışığı ideal (günde 6+ saat).\n🌱 Toprak: İyi drene, organik madde açısından zengin.\n✂️ Budama: İlkbahar başında ölü ve hastalıklı dalları kesin.\n🌡️ Sıcaklık: -20°C'ye kadar soğuğa dayanıklı.",
        "characteristics": {
            "yaprak_tipi": "Bileşik yaprak, 5-7 yaprakçık",
            "yaprak_kenari": "Testere dişli",
            "çiçek_rengi": "Koyu pembe, kırmızı",
            "çiçek_sayısı": "5 taç yaprak",
            "çiçek_çapı": "4-6 cm",
            "koku": "Hoş, yoğun gül kokusu",
            "boy": "60-120 cm",
            "kullanım": "Süs bitkisi, parfüm, gül suyu, şifalı bitkiler"
        },
        "image_urls": [],
        "plantnet_verified": True
    },
    {
        "scientific_name": "Rosa chinensis",
        "scientific_name_full": "Rosa chinensis Jacq.",
        "common_names": ["China Rose", "Çin Gülü", "Ay Gülü"],
        "family": "Rosaceae",
        "genus": "Rosa",
        "description": "Güneybatı Çin'e özgü, tekrar çiçeklenme ve hastalık direnci ile bilinen gül türüdür. Modern bahçe güllerinin atalarından biridir.",
        "habitat": "Verimli, iyi drene topraklarda yetişir. Sıcağa dayanıklıdır.",
        "care_instructions": "💧 Sulama: Haftada 2-3 kez, derin sulama.\n☀️ Işık: Tam güneş ışığı (günde 6-8 saat).\n🌱 Toprak: Verimli, gevşek, pH 6.0-6.5.\n🌸 Çiçeklenme: Tekrar çiçeklenme için solmuş çiçekleri kesin.\n🌡️ Sıcaklık: Sıcağa dayanıklı, 30°C+ tolere eder.",
        "characteristics": {
            "yaprak_tipi": "Bileşik, 3-5 parlak yaprakçık",
            "yaprak_şekli": "Oval",
            "çiçek_rengi": "Beyaz, pembe, kırmızı",
            "çiçek_tipi": "Tekli veya dolu",
            "çiçek_çapı": "5-10 cm",
            "boy": "90-180 cm",
            "çiçeklenme_dönemi": "İlkbahardan sonbahara (tekrarlayan)",
            "kullanım": "Süs bitkisi, çay yapımı"
        },
        "image_urls": [],
        "plantnet_verified": True
    },
    {
        "scientific_name": "Rosa damascena",
        "scientific_name_full": "Rosa damascena Mill.",
        "common_names": ["Damask Rose", "Şam Gülü", "Yağ Gülü"],
        "family": "Rosaceae",
        "genus": "Rosa",
        "description": "Antik bir gül çeşidi, uçucu yağ üretimi için değerlidir. Yoğun ve tatlı kokulu pembe ila açık kırmızı çiçeklere sahiptir.",
        "habitat": "İyi drene, kumlu-tınlı topraklarda yetişir. Tam güneş ışığı gerektirir.",
        "care_instructions": "💧 Sulama: Orta düzeyde, toprağın üst kısmı kuruduğunda sulayın.\n☀️ Işık: Tam güneş (günde 6-8 saat).\n🌱 Toprak: İyi drene, kumlu-tınlı, pH 6.5-7.0.\n🌹 Yağ Üretimi: Sabah erken saatlerde çiçek toplayın (en yoğun koku).\n🌡️ Sıcaklık: 15-25°C ideal.",
        "characteristics": {
            "yaprak_tipi": "Bileşik, 5-7 tüylü gri-yeşil yaprakçık",
            "çiçek_rengi": "Pembe ila açık kırmızı",
            "çiçek_tipi": "Çok yapraklı (dolu)",
            "çiçek_çapı": "6-8 cm",
            "koku": "Yoğun, tatlı, çiçeksi (attar of roses)",
            "boy": "120-180 cm",
            "çiçeklenme_dönemi": "Yaz (bir kez)",
            "kullanım": "Gül yağı, gül suyu, kozmetik, yemek"
        },
        "image_urls": [],
        "plantnet_verified": True
    },
    {
        "scientific_name": "Tulipa gesneriana",
        "scientific_name_full": "Tulipa gesneriana L.",
        "common_names": ["Garden Tulip", "Bahçe Lalesi"],
        "family": "Liliaceae",
        "genus": "Tulipa",
        "description": "İlkbaharda çiçeklenen, Orta Asya'ya özgü popüler bir lale türüdür. Hollanda'nın sembolüdür. Kırmızı, sarı, pembe, beyaz, mor ve çok renkli çeşitleri vardır.",
        "habitat": "İyi drene, verimli, nötr ila hafif alkali topraklarda yetişir. Tam güneş ışığı veya hafif gölge tercih eder.",
        "care_instructions": "💧 Sulama: İlkbaharda büyüme döneminde düzenli sulama, çiçek açtıktan sonra azaltın.\n☀️ Işık: Tam güneş ışığı ideal (günde 6+ saat).\n🌱 Toprak: İyi drene, kumlu veya tınlı, pH 6.5-7.5.\n🧅 Soğan: Sonbaharda 10-15 cm derinliğe dikin.\n🌡️ Sıcaklık: Soğuğa dayanıklı (-20°C), soğuk stratifikasyon gerektirir.",
        "characteristics": {
            "yaprak_tipi": "2-6 geniş, mızrak şeklinde, mumlu, mavimsi-yeşil",
            "yaprak_düzeni": "Rozet",
            "çiçek_rengi": "Kırmızı, sarı, pembe, beyaz, mor, çok renkli",
            "çiçek_şekli": "Kupa şeklinde, 6 taç yaprak",
            "çiçek_yüksekliği": "5-10 cm",
            "bitki_boyu": "25-60 cm",
            "çiçeklenme_dönemi": "Erken ilkbahar ile orta ilkbahar",
            "soğan": "Yeraltı depolama organı",
            "kullanım": "Süs bitkisi, kesme çiçek"
        },
        "image_urls": [],
        "plantnet_verified": True
    },
    {
        "scientific_name": "Tulipa acuminata",
        "scientific_name_full": "Tulipa acuminata Vahl ex Hornem.",
        "common_names": ["Horned Tulip", "Boynuzlu Lale", "Örümcek Lale"],
        "family": "Liliaceae",
        "genus": "Tulipa",
        "description": "Dar, bükümlü, uzun taç yaprakları ile ayırt edici bir lale türüdür. Örümcek benzeri görünümüyle dikkat çeker. Sarı-kırmızı çizgili çiçekleri vardır.",
        "habitat": "İyi drene topraklarda yetişir. Tam güneş ışığı gerektirir.",
        "care_instructions": "💧 Sulama: Orta düzeyde, fazla su vermekten kaçının.\n☀️ Işık: Tam güneş ışığı.\n🌱 Toprak: İyi drene, kumlu.\n🧅 Soğan: Sonbaharda 10 cm derinliğe dikin.\n🌡️ Sıcaklık: Soğuğa dayanıklı.",
        "characteristics": {
            "yaprak_tipi": "3-5 doğrusal, mumlu yaprak",
            "çiçek_rengi": "Sarı, kırmızı çizgili",
            "çiçek_şekli": "Örümcek benzeri, dar ve uzun taç yapraklar (10-15 cm)",
            "çiçek_özelliği": "Bükümlü ve kıvrımlı",
            "bitki_boyu": "40-50 cm",
            "çiçeklenme_dönemi": "Orta ilkbahar ile geç ilkbahar",
            "özel_özellik": "Çok nadir, süs amaçlı konuşma parçası",
            "kullanım": "Süs bitkisi, koleksiyonculuk"
        },
        "image_urls": [],
        "plantnet_verified": True
    },
    {
        "scientific_name": "Tulipa clusiana",
        "scientific_name_full": "Tulipa clusiana DC.",
        "common_names": ["Lady Tulip", "Kadın Lalesi", "Yıldız Lalesi"],
        "family": "Liliaceae",
        "genus": "Tulipa",
        "description": "İran ve Afganistan'a özgü zarif bir lale türüdür. Açıldığında yıldız şeklinde, beyaz taç yaprakları kırmızı dış yüzlü ve sarı merkezli çiçekler üretir.",
        "habitat": "İyi drene, kayalık topraklarda yetişir. Tam güneş ışığı tercih eder.",
        "care_instructions": "💧 Sulama: Az sulama, kuraklığa dayanıklı.\n☀️ Işık: Tam güneş ışığı.\n🌱 Toprak: İyi drene, kayalık, kumlu.\n🧅 Soğan: Sonbaharda dikin, doğallaşır (her yıl geri gelir).\n🌡️ Sıcaklık: Sıcağa dayanıklı, çok yıllık.",
        "characteristics": {
            "yaprak_tipi": "3-4 dar, doğrusal, gri-yeşil yaprak",
            "çiçek_rengi": "Beyaz (iç), kırmızı (dış), sarı merkez",
            "çiçek_şekli": "Yıldız şeklinde (açıldığında)",
            "çiçek_yüksekliği": "4-5 cm",
            "bitki_boyu": "20-30 cm",
            "çiçeklenme_dönemi": "Erken ilkbahar ile orta ilkbahar",
            "özel_özellik": "Doğallaşır, sıcağa dayanıklı, çok yıllık",
            "kullanım": "Kaya bahçeleri, doğallaştırma"
        },
        "image_urls": [],
        "plantnet_verified": True
    },
]

def seed_database():
    """Seed PostgreSQL with detailed plant data"""
    logger.info("="*60)
    logger.info("  SEEDING POSTGRESQL WITH PLANT DATA")
    logger.info("="*60)
    
    db = SessionLocal()
    try:
        added = 0
        updated = 0
        failed = 0
        
        for plant_data in SEED_PLANTS:
            try:
                scientific_name = plant_data["scientific_name"]
                logger.info(f"\n🌱 Processing: {scientific_name}")
                
                # Check if exists
                existing = plant_repository.get_plant_by_scientific_name(db, scientific_name)
                
                if existing:
                    logger.info(f"   Plant exists, updating...")
                    updated += 1
                else:
                    logger.info(f"   New plant, creating...")
                    added += 1
                
                # Create or update
                result = plant_repository.create_or_update_plant(db, plant_data)
                
                if result:
                    logger.info(f"   ✅ Success: {scientific_name}")
                else:
                    logger.error(f"   ❌ Failed: {scientific_name}")
                    failed += 1
                    
            except Exception as e:
                logger.error(f"   ❌ Error processing {plant_data.get('scientific_name')}: {e}")
                failed += 1
                continue
        
        logger.info("\n" + "="*60)
        logger.info("  SUMMARY")
        logger.info("="*60)
        logger.info(f"  Total plants: {len(SEED_PLANTS)}")
        logger.info(f"  ✅ Added: {added}")
        logger.info(f"  🔄 Updated: {updated}")
        logger.info(f"  ❌ Failed: {failed}")
        
        if failed == 0:
            logger.info("\n  🎉 Database seeding completed successfully!")
        else:
            logger.warning(f"\n  ⚠️  Completed with {failed} failures")
        
    except Exception as e:
        logger.error(f"❌ Seeding failed: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
