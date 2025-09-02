#!/usr/bin/env python3
"""
SmartBot.uz - AI Marketing Avtomat
O'z-o'zini boshqaruvchi AI tizimi

Bu skript har kuni soat 9:00 da avtomatik ishlaydigan tizim.
Hech qanday tugma bosish shart emas - barcha jarayonlar avtomatik.

Funktsiylari:
1. AI trendlarni tekshiradi
2. 5 ta SEO blog posti yaratadi
3. Ularni optimal vaqtlarda Telegram kanaliga yuboradi
"""

import os
import json
import time
import schedule
import threading
import logging
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any
import random
import re

# Try importing AI library
try:
    import google.generativeai as genai
except ImportError:
    genai = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ai_marketing.log'),
        logging.StreamHandler()
    ]
)

class AIMarketingAvtomat:
    def __init__(self):
        """Initialize AI Marketing Avtomat"""
        self.setup_config()
        self.setup_ai()
        self.setup_telegram()
        
    def setup_config(self):
        """Setup configuration"""
        self.data_dir = "data"
        self.blog_posts_file = os.path.join(self.data_dir, "blog.json")
        self.marketing_stats_file = os.path.join(self.data_dir, "marketing_stats.json")
        
        # Create data directory if not exists
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
        # Optimal posting times (when subscribers are most active)
        self.posting_times = [
            "09:00",  # 9:00 AM
            "12:30",  # 12:30 PM  
            "17:30",  # 5:30 PM
            "18:00",  # 6:00 PM
            "20:00"   # 8:00 PM
        ]
        
    def setup_ai(self):
        """Setup AI configuration"""
        self.gemini_api_key = os.environ.get("GEMINI_API_KEY")
        if self.gemini_api_key and genai:
            try:
                genai.configure(api_key=self.gemini_api_key)
                self.ai_model = genai.GenerativeModel('gemini-1.5-flash')
                logging.info("AI model initialized successfully")
            except Exception as e:
                logging.error(f"AI initialization failed: {e}")
                self.ai_model = None
        else:
            logging.warning("GEMINI_API_KEY not found or genai not available")
            self.ai_model = None
            
    def setup_telegram(self):
        """Setup Telegram configuration"""
        self.telegram_bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
        self.telegram_channel_id = os.environ.get("TELEGRAM_CHAT_ID") or os.environ.get("TELEGRAM_CHANNEL_ID")
        
        if not self.telegram_bot_token or not self.telegram_channel_id:
            logging.warning("Telegram credentials not configured properly")
            
    def get_current_trends(self) -> List[str]:
        """Get current trends in IT, AI, Telegram bots, automation"""
        trends = [
            "AI chatbotlar biznesda",
            "Telegram bot orqali savdo", 
            "Sun'iy intellekt ta'limda",
            "Biznes jarayonlarini avtomatlashtirish",
            "AI yordamchi xizmatlar",
            "Smart chatbot integratsiyasi",
            "Telegram marketing strategiyasi",
            "AI content generation",
            "Avtomatik mijozlar xizmati",
            "Digital transformatsiya AI bilan",
            "Telegram bot CRM tizimi",
            "AI analitika va hisobotlar",
            "Aqlli biznes yechimlar",
            "Voice AI assistentlar",
            "AI-powered e-commerce bots",
            "Chatbot savdo yordamchisi",
            "Telegram bot avtomatlashtirish",
            "AI mijozlar xizmati",
            "Smart business bots",
            "AI marketing strategiyalar"
        ]
        
        # Select 5 random trends for today
        selected_trends = random.sample(trends, 5)
        logging.info(f"Selected trends for today: {selected_trends}")
        return selected_trends
        
    def create_blog_post(self, trend: str) -> Dict[str, Any]:
        """Create SEO optimized blog post for a trend"""
        if not self.ai_model:
            logging.error("AI model not available for blog creation")
            return None
            
        try:
            prompt = f"""
            "{trend}" mavzusida o'zbek tilida professional SEO blog maqolasi yozing.

            Talablar:
            - 600-700 so'z 
            - 5-6 paragraf
            - Jozibador va SEO-optimallashtirilgan sarlavha
            - Kalit so'zlar: AI, bot, avtomatlashtirish, SmartBot.uz
            - Paragraflar qisqa va tushunarli
            - Professional uslubda
            - Oxirida majburiy: "SmartBot.uz — aqlli yechimlar, zamonaviy biznes uchun"
            
            Maqolani HTML formatida qaytaring, faqat <h2>, <p>, <ul>, <li> teglaridan foydalaning.
            """
            
            response = self.ai_model.generate_content(prompt)
            content = response.text
            
            # Extract title from content (first h2 tag or first line)
            title_match = re.search(r'<h2>(.*?)</h2>', content)
            if title_match:
                title = title_match.group(1)
            else:
                # Fallback: use first line as title
                lines = content.split('\n')
                title = lines[0].strip()
                if title.startswith('#'):
                    title = title.strip('# ')
                    
            # Create excerpt (first 200 characters without HTML tags)
            clean_content = re.sub(r'<[^>]+>', '', content)
            excerpt = clean_content[:200] + "..." if len(clean_content) > 200 else clean_content
            
            # Create slug from title
            slug = self.create_slug(title)
            
            blog_post = {
                "id": int(datetime.now().timestamp()),
                "title": title,
                "content": content,
                "excerpt": excerpt,
                "slug": slug,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "time": datetime.now().strftime("%H:%M:%S"),
                "trend": trend,
                "category": "AI Generated",
                "ai_generated": True,
                "posted_to_telegram": False,
                "telegram_scheduled_time": None
            }
            
            logging.info(f"Blog post created: {title}")
            return blog_post
            
        except Exception as e:
            logging.error(f"Error creating blog post for trend '{trend}': {e}")
            return None
            
    def create_slug(self, text: str) -> str:
        """Create URL-friendly slug from text"""
        # Convert to lowercase and replace non-alphanumeric chars with hyphens
        slug = re.sub(r'[^\w\s-]', '', text.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')
        
    def save_blog_posts(self, blog_posts: List[Dict[str, Any]]) -> bool:
        """Save blog posts to JSON file (existing blog.json format)"""
        try:
            # Load existing posts
            existing_posts = self.load_blog_posts()
            
            # Add new posts
            all_posts = existing_posts + blog_posts
            
            # Save to file
            with open(self.blog_posts_file, 'w', encoding='utf-8') as f:
                json.dump(all_posts, f, ensure_ascii=False, indent=2)
                
            logging.info(f"Saved {len(blog_posts)} new blog posts to {self.blog_posts_file}")
            return True
            
        except Exception as e:
            logging.error(f"Error saving blog posts: {e}")
            return False
            
    def load_blog_posts(self) -> List[Dict[str, Any]]:
        """Load existing blog posts"""
        try:
            if os.path.exists(self.blog_posts_file):
                with open(self.blog_posts_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            logging.error(f"Error loading blog posts: {e}")
            return []
            
    def schedule_telegram_posts(self, blog_posts: List[Dict[str, Any]]):
        """Schedule blog posts for Telegram at optimal times"""
        if not blog_posts:
            return
            
        # Assign posting times to blog posts
        for i, post in enumerate(blog_posts):
            if i < len(self.posting_times):
                scheduled_time = self.posting_times[i]
                post['telegram_scheduled_time'] = scheduled_time
                
                # Schedule the post
                schedule.every().day.at(scheduled_time).do(
                    self.post_to_telegram, post
                ).tag(f"post_{post['id']}")
                
                logging.info(f"Scheduled '{post['title']}' for {scheduled_time}")
                
    def post_to_telegram(self, blog_post: Dict[str, Any]):
        """Post blog to Telegram channel"""
        if not self.telegram_bot_token or not self.telegram_channel_id:
            logging.error("Telegram credentials not configured")
            return False
            
        try:
            # Format message
            message = f"""📢 YANGI MAQOLA: {blog_post['title']}

{blog_post['content'][:300]}...

👉 Batafsil: https://smartbot.uz/blog/{blog_post['slug']}

#AI #IT #SmartBotUz #Bot #Avtomatlashtirish"""

            # Send to Telegram
            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
            data = {
                'chat_id': self.telegram_channel_id,
                'text': message,
                'parse_mode': 'HTML',
                'disable_web_page_preview': False
            }
            
            response = requests.post(url, data=data, timeout=10)
            
            if response.status_code == 200:
                # Mark as posted
                blog_post['posted_to_telegram'] = True
                blog_post['telegram_posted_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Update the saved posts
                self.update_blog_post_status(blog_post)
                
                logging.info(f"Successfully posted '{blog_post['title']}' to Telegram")
                return True
            else:
                logging.error(f"Telegram post failed: {response.text}")
                return False
                
        except Exception as e:
            logging.error(f"Error posting to Telegram: {e}")
            return False
            
    def update_blog_post_status(self, updated_post: Dict[str, Any]):
        """Update blog post status in the file"""
        try:
            posts = self.load_blog_posts()
            for i, post in enumerate(posts):
                if post['id'] == updated_post['id']:
                    posts[i] = updated_post
                    break
                    
            with open(self.blog_posts_file, 'w', encoding='utf-8') as f:
                json.dump(posts, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logging.error(f"Error updating post status: {e}")
            
    def update_marketing_stats(self, posts_created: int, posts_scheduled: int):
        """Update marketing statistics"""
        try:
            stats = {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "time": datetime.now().strftime("%H:%M:%S"), 
                "posts_created": posts_created,
                "posts_scheduled": posts_scheduled,
                "ai_model_used": "gemini-1.5-flash",
                "status": "completed"
            }
            
            # Load existing stats
            existing_stats = []
            if os.path.exists(self.marketing_stats_file):
                with open(self.marketing_stats_file, 'r', encoding='utf-8') as f:
                    existing_stats = json.load(f)
                    
            existing_stats.append(stats)
            
            # Keep only last 30 days of stats
            existing_stats = existing_stats[-30:]
            
            with open(self.marketing_stats_file, 'w', encoding='utf-8') as f:
                json.dump(existing_stats, f, ensure_ascii=False, indent=2)
                
            logging.info("Marketing stats updated")
            
        except Exception as e:
            logging.error(f"Error updating marketing stats: {e}")
            
    def daily_content_generation(self):
        """Main function that runs daily at 9:00 AM"""
        logging.info("🚀 Starting daily AI Marketing Avtomat...")
        
        try:
            # 1. Get current trends
            trends = self.get_current_trends()
            
            # 2. Create blog posts for each trend
            blog_posts = []
            for trend in trends:
                post = self.create_blog_post(trend)
                if post:
                    blog_posts.append(post)
                time.sleep(2)  # Small delay between AI calls
                
            # 3. Save blog posts
            if blog_posts:
                success = self.save_blog_posts(blog_posts)
                if success:
                    logging.info(f"✅ Created and saved {len(blog_posts)} blog posts")
                    
                    # 4. Schedule Telegram posts
                    self.schedule_telegram_posts(blog_posts)
                    
                    # 5. Update statistics
                    self.update_marketing_stats(len(blog_posts), len(blog_posts))
                    
                    logging.info("🎯 Daily content generation completed successfully!")
                else:
                    logging.error("❌ Failed to save blog posts")
            else:
                logging.warning("⚠️ No blog posts were created")
                
        except Exception as e:
            logging.error(f"❌ Daily content generation failed: {e}")
            
    def run_scheduler(self):
        """Run the scheduler in background"""
        logging.info("🤖 AI Marketing Avtomat started - waiting for scheduled time...")
        
        # Schedule daily content generation at 9:00 AM
        schedule.every().day.at("09:00").do(self.daily_content_generation)
        
        # For immediate testing - uncomment next line
        # self.daily_content_generation()
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
            
    def start(self):
        """Start the AI Marketing Avtomat system"""
        logging.info("🚀 Initializing SmartBot.uz AI Marketing Avtomat...")
        
        # Run scheduler in background thread
        scheduler_thread = threading.Thread(target=self.run_scheduler, daemon=True)
        scheduler_thread.start()
        
        logging.info("✅ AI Marketing Avtomat is running!")
        logging.info("📅 Scheduled daily content generation at 09:00")
        logging.info("🔄 System is now autonomous - no manual intervention needed!")
        
        # Keep main thread alive
        try:
            while True:
                time.sleep(3600)  # Sleep for 1 hour
        except KeyboardInterrupt:
            logging.info("🛑 AI Marketing Avtomat stopped by user")

def main():
    """Main entry point"""
    try:
        # Check for required environment variables
        required_env = ["GEMINI_API_KEY", "TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"]
        missing_env = [env for env in required_env if not os.environ.get(env)]
        
        if missing_env:
            logging.error(f"Missing environment variables: {', '.join(missing_env)}")
            logging.error("Please set these in your Replit Secrets")
            return
            
        # Start the avtomat
        avtomat = AIMarketingAvtomat()
        avtomat.start()
        
    except Exception as e:
        logging.error(f"Failed to start AI Marketing Avtomat: {e}")

if __name__ == "__main__":
    main()