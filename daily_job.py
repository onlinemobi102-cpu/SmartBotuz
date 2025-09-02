#!/usr/bin/env python3
"""
SmartBot.uz AI Marketing Daily Job
Har kuni avtomatik ravishda blog postlari yaratadi va Telegram kanaliga yuboradi
"""

import os
import sys
import time
import schedule
import threading
import requests
import json
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ai_marketing.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class AIMarketingBot:
    def __init__(self):
        """Initialize AI Marketing Bot"""
        self.base_url = "http://localhost:5000"  # SmartBot.uz server URL
        self.admin_password = os.environ.get("ADMIN_PASSWORD", "smartbot123")
        
        # Optimal posting times (O'zbekiston vaqti)
        self.posting_times = [
            "09:00",  # Ertalab ish boshlanishi
            "12:30",  # Tushlik vaqti
            "17:30",  # Ish tugashi
            "18:00",  # Kechqurun faol vaqt
            "20:00"   # Kechki faol vaqt
        ]
        
        # Session for admin authentication
        self.session = requests.Session()
        self.authenticated = False
        
    def login_admin(self):
        """Admin panelga kirish"""
        try:
            # Admin login sahifasiga so'rov
            login_url = f"{self.base_url}/admin/login"
            login_data = {"password": self.admin_password}
            
            response = self.session.post(login_url, data=login_data)
            
            if response.status_code == 200 and "dashboard" in response.text.lower():
                self.authenticated = True
                logger.info("Admin panelga muvaffaqiyatli kirildi")
                return True
            else:
                logger.error("Admin panelga kirishda xatolik")
                return False
                
        except Exception as e:
            logger.error(f"Admin login xatolik: {e}")
            return False
    
    def run_ai_marketing(self):
        """AI Marketing jarayonini ishga tushirish"""
        try:
            if not self.authenticated:
                if not self.login_admin():
                    logger.error("Admin autentifikatsiyasi muvaffaqiyatsiz")
                    return False
            
            # AI Marketing run endpoint'ga so'rov
            marketing_url = f"{self.base_url}/admin/ai/marketing/run"
            
            logger.info("AI Marketing jarayonini boshlamoqda...")
            response = self.session.post(marketing_url)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    posts_count = data.get('count', 0)
                    logger.info(f"✅ Muvaffaqiyat! {posts_count} ta yangi blog post yaratildi va Telegram kanaliga yuborildi")
                    
                    # Created posts haqida ma'lumot
                    posts = data.get('posts', [])
                    for i, post in enumerate(posts, 1):
                        logger.info(f"{i}. {post.get('title', 'Nomsiz post')}")
                    
                    return True
                else:
                    error = data.get('error', 'Noma\'lum xatolik')
                    logger.error(f"❌ AI Marketing xatolik: {error}")
                    return False
            else:
                logger.error(f"Server xatolik: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"AI Marketing jarayonida xatolik: {e}")
            return False
    
    def schedule_daily_jobs(self):
        """Kunlik ishlarni rejalashtirish"""
        logger.info("Kunlik AI Marketing ishlarini rejalashtirmoqda...")
        
        # Har kuni ertalab 9:00 da ishga tushirish
        schedule.every().day.at("09:00").do(self.run_ai_marketing)
        
        logger.info("Rejalashtirilgan ishlar:")
        logger.info("- Har kuni 09:00 da AI Marketing avtomatik ishga tushadi")
        logger.info("- 5 ta trend blog post yaratadi")
        logger.info("- Telegram kanaliga yuboradi")
    
    def run_scheduler(self):
        """Scheduler ni ishga tushirish"""
        logger.info("🤖 SmartBot.uz AI Marketing Bot ishga tushmoqda...")
        
        # Kunlik ishlarni rejalashtirish
        self.schedule_daily_jobs()
        
        logger.info("⏰ Scheduler ishga tushdi. Keyingi ish: 09:00")
        
        # Scheduler sikl
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Har daqiqada tekshirish
                
                # Har soatda status log
                current_time = datetime.now().strftime("%H:%M")
                if current_time.endswith(":00"):
                    next_run = schedule.next_run()
                    if next_run:
                        logger.info(f"⏰ Keyingi AI Marketing: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
                        
            except KeyboardInterrupt:
                logger.info("🛑 Scheduler to'xtatildi")
                break
            except Exception as e:
                logger.error(f"Scheduler xatolik: {e}")
                time.sleep(300)  # 5 daqiqa kutish va qayta urinish

def main():
    """Asosiy funksiya"""
    print("🚀 SmartBot.uz AI Marketing Bot")
    print("=" * 50)
    
    # Environment variables tekshirish
    required_env = ["GEMINI_API_KEY", "TELEGRAM_BOT_TOKEN", "TELEGRAM_CHANNEL_ID"]
    missing_env = [env for env in required_env if not os.environ.get(env)]
    
    if missing_env:
        print(f"❌ Quyidagi environment variables yo'q: {', '.join(missing_env)}")
        print("Iltimos, .env faylida sozlang")
        sys.exit(1)
    
    # AI Marketing Bot ni ishga tushirish
    bot = AIMarketingBot()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--run-once":
        # Bir marta ishga tushirish (test uchun)
        print("🧪 Test rejimi: AI Marketing bir marta ishga tushadi...")
        success = bot.run_ai_marketing()
        if success:
            print("✅ Test muvaffaqiyatli yakunlandi!")
        else:
            print("❌ Test muvaffaqiyatsiz!")
        sys.exit(0 if success else 1)
    
    # Doimiy scheduler rejimi
    try:
        bot.run_scheduler()
    except KeyboardInterrupt:
        print("\n🛑 AI Marketing Bot to'xtatildi")
    except Exception as e:
        print(f"❌ Fatal xatolik: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()