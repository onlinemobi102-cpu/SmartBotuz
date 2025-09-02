import os
from flask import Flask, render_template, request, flash, redirect, url_for, jsonify, session
from werkzeug.utils import secure_filename
from functools import wraps
import logging
import re
import requests
import json
import uuid

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# File upload configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "smartbot-uz-secret-key")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# Admin Configuration
ADMIN_PASSWORD = "smartbot123"

# Data storage files
DATA_DIR = "data"
SERVICES_FILE = os.path.join(DATA_DIR, "services.json")
PORTFOLIO_FILE = os.path.join(DATA_DIR, "portfolio.json")
BLOG_FILE = os.path.join(DATA_DIR, "blog.json")
MESSAGES_FILE = os.path.join(DATA_DIR, "messages.json")

# Create directories if they don't exist
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Utility functions
def create_slug(text):
    """Simple slug generation function"""
    # Convert to lowercase and replace non-alphanumeric chars with hyphens
    slug = re.sub(r'[^\w\s-]', '', text.lower())
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Initialize data files with default content
def initialize_data_files():
    if not os.path.exists(SERVICES_FILE):
        default_services = [
            {
                "id": 1,
                "title": "Telegram Bot Yaratish",
                "description": "Telegram botlarni noldan yaratamiz - mijozlar bilan aloqa, buyurtma qabul qilish, avtomatlashtirish",
                "icon": "fas fa-robot",
                "price": "500,000 so'mdan"
            },
            {
                "id": 2,
                "title": "Chatbot Integratsiya",
                "description": "Saytingizga AI chatbot qo'shamiz - 24/7 mijozlar bilan suhbat, savolga javob berish",
                "icon": "fas fa-comments",
                "price": "300,000 so'mdan"
            }
        ]
        save_data(SERVICES_FILE, default_services)
    
    if not os.path.exists(PORTFOLIO_FILE):
        default_portfolio = [
            {
                "id": 1,
                "title": "E-commerce Bot",
                "description": "Telegram orqali mahsulot sotish va buyurtmalarni boshqarish",
                "image": "portfolio-1.jpg",
                "tags": ["Telegram", "E-commerce", "Bot"],
                "category": "bot"
            },
            {
                "id": 2,
                "title": "Ta'lim Boti",
                "description": "O'quvchilar uchun testlar va natijalarni boshqarish tizimi",
                "image": "portfolio-2.jpg", 
                "tags": ["Telegram", "Education", "Test"],
                "category": "bot"
            }
        ]
        save_data(PORTFOLIO_FILE, default_portfolio)
        
    if not os.path.exists(BLOG_FILE):
        default_blog = [
            {
                "id": 1,
                "title": "Telegram Bot yaratish bo'yicha boshlang'ich qo'llanma",
                "content": "Telegram botlar biznes uchun qanday foydali...",
                "excerpt": "Telegram botlar haqida asosiy ma'lumotlar",
                "category": "Qo'llanma",
                "date": "2024-03-15",
                "image": "blog-1.jpg"
            }
        ]
        save_data(BLOG_FILE, default_blog)
    
    # Initialize messages file
    if not os.path.exists(MESSAGES_FILE):
        save_data(MESSAGES_FILE, [])

def load_data(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def save_data(filename, data):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        app.logger.error(f"Failed to save data to {filename}: {e}")
        return False

def save_message(name, email, phone, service, budget, message):
    """Save contact message to JSON file"""
    from datetime import datetime
    
    messages = load_data(MESSAGES_FILE)
    new_id = max([m.get('id', 0) for m in messages], default=0) + 1
    
    new_message = {
        'id': new_id,
        'name': name,
        'email': email,
        'phone': phone if phone else '',
        'service': service if service else '',
        'budget': budget if budget else '',
        'message': message,
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'status': 'yangi',  # yangi, ko'rilgan, javob_berilgan
        'telegram_sent': False
    }
    
    messages.append(new_message)
    return save_data(MESSAGES_FILE, messages)

# Initialize data files on startup
initialize_data_files()

# Admin authentication decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def send_telegram_message(message):
    """Send message to Telegram bot"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        app.logger.warning("Telegram credentials not configured")
        return False
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': 'HTML'
        }
        response = requests.post(url, data=data, timeout=10)
        return response.status_code == 200
    except Exception as e:
        app.logger.error(f"Failed to send Telegram message: {e}")
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/portfolio')
def portfolio():
    return render_template('portfolio.html')

@app.route('/portfolio/<project_slug>')
def portfolio_detail(project_slug):
    """Portfolio detail pages using JSON data"""
    
    # Load portfolio data from JSON
    portfolio = load_data(PORTFOLIO_FILE)
    
    # Find project by slug
    project = None
    for p in portfolio:
        if p.get('slug') == project_slug:
            project = p
            break
    
    if not project:
        flash("Loyiha topilmadi!", "error")
        return redirect(url_for('portfolio'))
    
    # Set default values for missing fields
    project.setdefault('gradient', 'primary')
    project.setdefault('icon', 'fas fa-laptop-code')
    project.setdefault('client', 'Mijoz')
    project.setdefault('duration', 'N/A')
    project.setdefault('price', 'Kelishilgan narxda')
    project.setdefault('status', 'Bajarildi')
    project.setdefault('problem', project.get('description', ''))
    project.setdefault('solution', project.get('description', ''))
    project.setdefault('features', [])
    project.setdefault('results', [])
    project.setdefault('technologies', [])
    
    return render_template('portfolio/detail.html', project=project)
            'duration': "2 hafta",
            'price': "2,500,000 so'm",
            'status': "Muvaffaqiyatli yakunlandi",
            'category': "Telegram Bot",
            'gradient': "primary",
            'icon': "fab fa-telegram",
            'problem': "Do'kon egasi har kuni onlayn buyurtmalarni qo'lda qayd qilardi. Mijozlar bilan WhatsApp orqali muloqot qilish vaqtni ko'p olardi, xatolar tez-tez ro'y berardi va sotuv jarayoni sekin edi.",
            'solution': "Telegram bot orqali to'liq avtomatlashtirilgan e-commerce tizimi yaratildi. Mijozlar katalogni ko'rishi, mahsulot tanlashi, buyurtma berishi va to'lov qilishi mumkin bo'ldi.",
            'features': [
                "Mahsulotlar katalogi va kategoriyalar",
                "Savat va buyurtma boshqaruvi", 
                "Click/Payme to'lov integratsiyasi",
                "Admin panel buyurtmalarni kuzatish uchun",
                "SMS va email xabarnomalar"
            ],
            'results': [
                "Buyurtma berish vaqti 10 daqiqadan 2 daqiqaga qisqardi",
                "Sotuv miqdori 150% oshdi",
                "Mijozlar qulayligi 90% yaxshilandi",
                "Operatsion xarajatlar 40% kamaydi"
            ],
            'technologies': ["Python", "aiogram", "Telegram Bot API", "Click API", "Payme API", "PostgreSQL", "Redis"]
        },
        'education-bot': {
            'title': "Ta'lim Boti",
            'short_description': "O'quvchilar uchun testlar va natijalarni boshqarish tizimi",
            'client': "EduCenter Academy",
            'duration': "3 hafta", 
            'price': "3,500,000 so'm",
            'status': "Muvaffaqiyatli yakunlandi",
            'category': "Telegram Bot",
            'gradient': "success",
            'icon': "fas fa-graduation-cap",
            'problem': "Ta'lim markazi testlarni qog'ozda o'tkazardi. Natijalarni tekshirish va baholar qo'yish ko'p vaqt olardi. O'quvchilar natijalarini kechikib bilar edi.",
            'solution': "Telegram bot orqali onlayn test tizimi yaratildi. O'quvchilar testlarni topshirishi, darhol natijani bilishi va o'qituvchilar hisobotlarni real vaqtda olishi mumkin.",
            'features': [
                "Ko'p tanlovli va ochiq savollar tizimi",
                "Real vaqtda natijalarni ko'rsatish",
                "O'qituvchilar uchun admin panel",
                "Excel formatda hisobotlar",
                "Darajalar va sertifikatlar tizimi"
            ],
            'results': [
                "Test topshirish vaqti 50% qisqardi",
                "O'qituvchilar ish yukini 60% kamaytirdi", 
                "O'quvchilar faolligi 200% oshdi",
                "Xatolar 95% kamaydi"
            ],
            'technologies': ["Python", "aiogram", "SQLite", "Telegram Bot API", "Excel API", "PDF Generator"]
        },
        'restaurant-bot': {
            'title': "Restoran Boti",
            'short_description': "Ovqat buyurtma berish va yetkazib berish xizmati",
            'client': "Osh Markazi",
            'duration': "1.5 hafta",
            'price': "2,000,000 so'm", 
            'status': "Muvaffaqiyatli yakunlandi",
            'category': "Telegram Bot",
            'gradient': "warning",
            'icon': "fas fa-utensils",
            'problem': "Restoran telefon orqali buyurtma qabul qilardi. Qo'ng'iroqlar ko'p bo'lganda operatorlar yetmay qolardi va mijozlar kutishga majbur bo'lardi.",
            'solution': "Telegram bot orqali 24/7 avtomatik buyurtma qabul qilish tizimi ishlab chiqildi. Mijozlar menuni ko'rishi, buyurtma berishi va yetkazib berish vaqtini bilishi mumkin.",
            'features': [
                "To'liq menu va narxlar",
                "Geolokatsiya va yetkazib berish zonalari",
                "Buyurtma holati kuzatuvi",
                "Fikr-mulohazalar tizimi",
                "Aksiya va chegirmalar"
            ],
            'results': [
                "Buyurtmalar soni 180% oshdi",
                "Mijozlar kutish vaqti 0ga tushdi",
                "Operator xarajatlari 70% kamaydi",
                "Mijozlar qoniqish darajasi 95% bo'ldi"
            ],
            'technologies': ["Python", "aiogram", "Google Maps API", "Firebase", "Telegram Bot API"]
        },
        'bank-chatbot': {
            'title': "Bank Chatbot", 
            'short_description': "24/7 mijozlar xizmati va bank operatsiyalari",
            'client': "InnoBank",
            'duration': "4 hafta",
            'price': "8,500,000 so'm",
            'status': "Muvaffaqiyatli yakunlandi", 
            'category': "AI Chatbot",
            'gradient': "info",
            'icon': "fas fa-comments",
            'problem': "Bank mijozlari balansini tekshirish, o'tkazmalar tarixi va kredit ma'lumotlari uchun filialga borish yoki qo'ng'iroq qilishga majbur edi. Call markazda navbat uzoq edi.",
            'solution': "AI chatbot orqali mijozlar 24/7 bank xizmatlaridan foydalanishi, balansini tekshirishi, o'tkazmalar qilishi va kredit haqida ma'lumot olishi mumkin bo'ldi.",
            'features': [
                "Balans va kartalar ma'lumoti",
                "O'tkazmalar tarixi", 
                "Kredit kalkulyatori",
                "Valyuta kurslari",
                "FAQ va qo'llab-quvvatlash"
            ],
            'results': [
                "Call markaz yukini 60% kamaytirdi",
                "Mijozlar qoniqish darajasi 85% oshdi",
                "Operatsion xarajatlar 45% kamaydi",
                "Xizmat sifati 24/7 ga uzaydi"
            ],
            'technologies': ["Python", "OpenAI API", "Bank API", "NLP", "Flask", "PostgreSQL"]
        },
        'support-bot': {
            'title': "Qo'llab-quvvatlash Boti",
            'short_description': "24/7 mijozlar xizmati va muammolarni hal qilish",
            'client': "TechSupport Pro",
            'duration': "2 hafta",
            'price': "3,000,000 so'm",
            'status': "Muvaffaqiyatli yakunlandi",
            'category': "Support Bot", 
            'gradient': "danger",
            'icon': "fas fa-headset",
            'problem': "Kompaniya mijozlarning savollariga javob berish uchun 5 nafar operatorni ish haqi to'lashi kerak edi. Tunda va dam olish kunlarida xizmat yo'q edi.",
            'solution': "AI chatbot orqali avtomatik javoblar tizimi yaratildi. Bot umumiy savollarni hal qiladi, murakkab holatlarda operatorga yo'naltiradi.",
            'features': [
                "FAQ avtomatik javoblar",
                "Muammolarni kategoriyalash",
                "Operator bilan bog'lash tizimi",
                "Hisobotlar va statistika",
                "Ko'p tilda qo'llab-quvvatlash"
            ],
            'results': [
                "Support so'rovlarini 80% avtomatlashtirdi",
                "Operatorlar ish yukini 70% kamaytirdi",
                "Mijozlar 24/7 yordam oladi",
                "Javob berish vaqti 5 daqiqaga tushdi"
            ],
            'technologies': ["Python", "aiogram", "NLP", "Machine Learning", "Flask", "SQLite"]
        },
        'crm-automation': {
            'title': "CRM Avtomatlashtirish",
            'short_description': "Mijozlar bilan ishlash jarayonini avtomatlashtirish",
            'client': "SalesForce Uzbekistan", 
            'duration': "6 hafta",
            'price': "12,000,000 so'm",
            'status': "Muvaffaqiyatli yakunlandi",
            'category': "Business Automation",
            'gradient': "dark",
            'icon': "fas fa-cogs",
            'problem': "Sotuvchilar mijozlar ma'lumotlarini Excel'da saqlardi. Lead'lar bilan ishlash jarayoni tartibsiz edi va ko'p imkoniyatlar yo'qotilardi.",
            'solution': "To'liq avtomatlashtirilgan CRM tizimi yaratildi. Lead'larni boshqarish, avtomatik email yuborish va sotuvchilar faoliyatini kuzatish mumkin.",
            'features': [
                "Lead'lar boshqaruvi va pipeline",
                "Avtomatik email marketing",
                "Hisobotlar va analytics",
                "Telegram integratsiyasi",
                "Mobil ilova"
            ],
            'results': [
                "Sotuv samaradorligi 120% oshdi",
                "Lead'larni yo'qotish 60% kamaydi",
                "Hisobotlar vaqti 90% qisqardi",
                "Jamoaviy ish sifati 80% yaxshilandi"
            ],
            'technologies': ["Python", "Django", "PostgreSQL", "Redis", "Celery", "Email API", "Telegram API"]
        },
        'reports-automation': {
            'title': "Hisobot Avtomatlashtirish",
            'short_description': "Ma'lumotlar analizi va avtomatik hisobotlar tizimi",
            'client': "DataFlow Analytics",
            'duration': "5 hafta", 
            'price': "9,500,000 so'm",
            'status': "Muvaffaqiyatli yakunlandi",
            'category': "Data Analytics",
            'gradient': "secondary", 
            'icon': "fas fa-chart-bar",
            'problem': "Kompaniya har oyning oxirida hisobotlarni qo'lda tayyorlashi kerak edi. Bu jarayon 3-4 kun vaqt olardi va xatolar ko'p ro'y berardi.",
            'solution': "Avtomatik hisobot tizimi yaratildi. Ma'lumotlar real vaqtda tahlil qilinadi va hisobotlar avtomatik ravishda yaratiladi va email orqali yuboriladi.",
            'features': [
                "Real-time dashboard",
                "Avtomatik hisobot yaratish",
                "Email/Telegram xabarnomalar",
                "Excel/PDF export",
                "Custom analytics"
            ],
            'results': [
                "Hisobot tayyorlash vaqti 95% qisqardi",
                "Xatolar 90% kamaydi",
                "Ma'lumotlarning aniqligi 99% bo'ldi",
                "Qaror qabul qilish tezlashdi"
            ],
            'technologies': ["Python", "Pandas", "Plotly", "Flask", "PostgreSQL", "Celery", "Email API"]
        },
        'corporate-website': {
            'title': "Korporativ Sayt",
            'short_description': "Zamonaviy korporativ web sayt CMS bilan",
            'client': "TechCorp Solutions",
            'duration': "3 hafta",
            'price': "5,500,000 so'm",
            'status': "Muvaffaqiyatli yakunlandi",
            'category': "Web Development",
            'gradient': "primary",
            'icon': "fas fa-globe",
            'problem': "Kompaniya eski va noqulay web saytga ega edi. Mijozlar saytdan kerakli ma'lumotni topa olmaydi va kompaniya professional ko'rinmaydi.",
            'solution': "Zamonaviy, responsive va SEO optimizatsiya qilingan korporativ web sayt yaratildi. Admin panel orqali kontent boshqarish mumkin.",
            'features': [
                "Responsive dizayn",
                "CMS admin panel", 
                "SEO optimizatsiya",
                "Google Analytics",
                "Contact formalar"
            ],
            'results': [
                "Sayt trafigi 300% oshdi",
                "Konversiya 150% yaxshilandi",
                "Google'da reytingi oshdi",
                "Mijozlardan murojaatlar ko'paydi"
            ],
            'technologies': ["HTML5", "CSS3", "JavaScript", "Python", "Flask", "PostgreSQL", "Bootstrap"]
        },
        'ecommerce-platform': {
            'title': "E-commerce Platform",
            'short_description': "To'liq funktsional onlayn do'kon platformasi",
            'client': "MegaShop Online",
            'duration': "8 hafta",
            'price': "18,500,000 so'm", 
            'status': "Muvaffaqiyatli yakunlandi",
            'category': "E-commerce",
            'gradient': "success",
            'icon': "fas fa-shopping-cart",
            'problem': "Kompaniya mahsulotlarini faqat offline sotardi. Onlayn bozorga kirish va ko'proq mijozlarga yetish kerak edi.",
            'solution': "To'liq funktsional e-commerce platforma yaratildi. Mahsulotlar katalogi, buyurtma tizimi, to'lov va yetkazib berish integratsiyasi.",
            'features': [
                "Mahsulotlar katalogi va qidiruv",
                "Savat va buyurtma tizimi",
                "To'lov tizimi (Click/Payme)",
                "Admin panel",
                "Hisobotlar va analytics"
            ],
            'results': [
                "Onlayn sotuv 0'dan boshlanib 50M so'mga yetdi",
                "Mijozlar bazasi 1000+ ga oshdi", 
                "Offline sotuv ham 30% oshdi",
                "ROI 6 oyda 400% bo'ldi"
            ],
            'technologies': ["Python", "Django", "PostgreSQL", "Redis", "Payment APIs", "AWS", "Bootstrap"]
        }
    }
    
    project = projects.get(project_id)
    if not project:
        flash("Loyiha topilmadi!", "error")
        return redirect(url_for('portfolio'))
    
    return render_template('portfolio/detail.html', project=project)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        service = request.form.get('service', '')
        budget = request.form.get('budget', '')
        message = request.form.get('message', '').strip()
        
        # Validation errors
        errors = []
        
        # Required field validation
        if not name:
            errors.append('Ism va familiya majburiy')
        elif len(name) < 2:
            errors.append('Ism kamida 2 harf bo\'lishi kerak')
            
        if not email:
            errors.append('Email manzili majburiy')
        elif not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            errors.append('Email manzili noto\'g\'ri formatda')
            
        if not message:
            errors.append('Xabar matni majburiy')
        elif len(message) < 10:
            errors.append('Xabar kamida 10 harf bo\'lishi kerak')
            
        # Phone number validation (if provided)
        if phone and not re.match(r'^\+998\s\d{2}\s\d{3}\s\d{2}\s\d{2}$', phone):
            errors.append('Telefon raqami noto\'g\'ri formatda. Namuna: +998 90 123 45 67')
        
        if errors:
            for error in errors:
                flash(error, 'error')
        else:
            # Create Telegram message
            telegram_message = f"""📝 <b>Yangi murojaat - SmartBot.uz</b>

👤 <b>Ism:</b> {name}
📧 <b>Email:</b> {email}"""
            
            if phone:
                telegram_message += f"\n📞 <b>Telefon:</b> {phone}"
            if service:
                telegram_message += f"\n🔧 <b>Xizmat:</b> {service}"
            if budget:
                telegram_message += f"\n💰 <b>Byudjet:</b> {budget}"
            
            telegram_message += f"\n💬 <b>Xabar:</b> {message}"
            telegram_message += f"\n\n⏰ <b>Vaqt:</b> {request.environ.get('REQUEST_TIME', 'N/A')}"
            
            # Save message to JSON file
            message_saved = save_message(name, email, phone, service, budget, message)
            
            # Send to Telegram
            telegram_sent = send_telegram_message(telegram_message)
            
            # Update message with telegram status if saved
            if message_saved and telegram_sent:
                messages = load_data(MESSAGES_FILE)
                if messages:
                    messages[-1]['telegram_sent'] = True
                    save_data(MESSAGES_FILE, messages)
            
            # Log the submission
            app.logger.info(f'New contact form submission from {name} ({email}) - Saved: {message_saved}, Telegram: {telegram_sent}')
            
            # Flash success message
            if telegram_sent:
                flash('Xabaringiz muvaffaqiyatli yuborildi! 24 soat ichida siz bilan bog\'lanamiz.', 'success')
            else:
                flash('Xabaringiz qabul qilindi! Tez orada siz bilan bog\'lanamiz.', 'success')
            
            # If it's an AJAX request, return JSON response
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'success': True, 
                    'message': 'Xabaringiz muvaffaqiyatli yuborildi! 24 soat ichida siz bilan bog\'lanamiz.'
                })
            return redirect(url_for('contact'))
    
    return render_template('contact.html')

@app.route('/blog')
def blog():
    return render_template('blog.html')

# ========================
# ADMIN ROUTES
# ========================

@app.route('/admin')
def admin_redirect():
    if session.get('admin'):
        return redirect(url_for('admin_dashboard'))
    return redirect(url_for('admin_login'))

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password', '')
        if password == ADMIN_PASSWORD:
            session['admin'] = True
            flash("Kirish muvaffaqiyatli amalga oshirildi!", "success")
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Noto'g'ri parol!", "error")
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    flash("Tizimdan chiqish amalga oshirildi.", "info")
    return redirect(url_for('index'))

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    services_count = len(load_data(SERVICES_FILE))
    portfolio_count = len(load_data(PORTFOLIO_FILE))
    blog_count = len(load_data(BLOG_FILE))
    messages_count = len(load_data(MESSAGES_FILE))
    
    # Count new messages
    messages = load_data(MESSAGES_FILE)
    new_messages_count = len([m for m in messages if m.get('status') == 'yangi'])
    
    stats = {
        'services': services_count,
        'portfolio': portfolio_count,
        'blog': blog_count,
        'messages': messages_count,
        'new_messages': new_messages_count
    }
    return render_template('admin/dashboard.html', stats=stats)

# ========================
# SERVICES MANAGEMENT
# ========================

@app.route('/admin/services')
@admin_required
def admin_services():
    services = load_data(SERVICES_FILE)
    return render_template('admin/services.html', services=services)

@app.route('/admin/services/add', methods=['GET', 'POST'])
@admin_required
def admin_services_add():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        icon = request.form.get('icon', '').strip()
        price = request.form.get('price', '').strip()
        
        if not all([title, description, icon, price]):
            flash("Barcha maydonlarni to'ldiring!", "error")
        else:
            services = load_data(SERVICES_FILE)
            new_id = max([s.get('id', 0) for s in services], default=0) + 1
            
            new_service = {
                'id': new_id,
                'title': title,
                'description': description,
                'icon': icon,
                'price': price
            }
            
            services.append(new_service)
            if save_data(SERVICES_FILE, services):
                flash("Yangi xizmat qo'shildi!", "success")
                return redirect(url_for('admin_services'))
            else:
                flash("Xatolik yuz berdi!", "error")
    
    return render_template('admin/services_form.html')

@app.route('/admin/services/edit/<int:service_id>', methods=['GET', 'POST'])
@admin_required
def admin_services_edit(service_id):
    services = load_data(SERVICES_FILE)
    service = next((s for s in services if s.get('id') == service_id), None)
    
    if not service:
        flash("Xizmat topilmadi!", "error")
        return redirect(url_for('admin_services'))
    
    if request.method == 'POST':
        service['title'] = request.form.get('title', '').strip()
        service['description'] = request.form.get('description', '').strip()
        service['icon'] = request.form.get('icon', '').strip()
        service['price'] = request.form.get('price', '').strip()
        
        if save_data(SERVICES_FILE, services):
            flash("Xizmat yangilandi!", "success")
            return redirect(url_for('admin_services'))
        else:
            flash("Xatolik yuz berdi!", "error")
    
    return render_template('admin/services_form.html', service=service)

@app.route('/admin/services/delete/<int:service_id>')
@admin_required
def admin_services_delete(service_id):
    services = load_data(SERVICES_FILE)
    services = [s for s in services if s.get('id') != service_id]
    
    if save_data(SERVICES_FILE, services):
        flash("Xizmat o'chirildi!", "success")
    else:
        flash("Xatolik yuz berdi!", "error")
    
    return redirect(url_for('admin_services'))

# ========================
# PORTFOLIO MANAGEMENT
# ========================

@app.route('/admin/portfolio')
@admin_required
def admin_portfolio():
    portfolio = load_data(PORTFOLIO_FILE)
    return render_template('admin/portfolio.html', portfolio=portfolio)

@app.route('/admin/portfolio/add', methods=['GET', 'POST'])
@admin_required
def admin_portfolio_add():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        image = request.form.get('image', '').strip()
        tags = request.form.get('tags', '').strip()
        category = request.form.get('category', '').strip()
        
        if not all([title, description, category]):
            flash("Majburiy maydonlarni to'ldiring!", "error")
        else:
            portfolio = load_data(PORTFOLIO_FILE)
            new_id = max([p.get('id', 0) for p in portfolio], default=0) + 1
            
            # Process tags
            tags_list = [tag.strip() for tag in tags.split(',') if tag.strip()] if tags else []
            
            new_project = {
                'id': new_id,
                'title': title,
                'description': description,
                'image': image if image else 'default-portfolio.jpg',
                'tags': tags_list,
                'category': category
            }
            
            portfolio.append(new_project)
            if save_data(PORTFOLIO_FILE, portfolio):
                flash("Yangi loyiha qo'shildi!", "success")
                return redirect(url_for('admin_portfolio'))
            else:
                flash("Xatolik yuz berdi!", "error")
    
    return render_template('admin/portfolio_form.html')

@app.route('/admin/portfolio/edit/<int:project_id>', methods=['GET', 'POST'])
@admin_required
def admin_portfolio_edit(project_id):
    portfolio = load_data(PORTFOLIO_FILE)
    project = next((p for p in portfolio if p.get('id') == project_id), None)
    
    if not project:
        flash("Loyiha topilmadi!", "error")
        return redirect(url_for('admin_portfolio'))
    
    if request.method == 'POST':
        project['title'] = request.form.get('title', '').strip()
        project['description'] = request.form.get('description', '').strip()
        project['image'] = request.form.get('image', '').strip() or 'default-portfolio.jpg'
        project['category'] = request.form.get('category', '').strip()
        
        # Process tags
        tags = request.form.get('tags', '').strip()
        project['tags'] = [tag.strip() for tag in tags.split(',') if tag.strip()] if tags else []
        
        if save_data(PORTFOLIO_FILE, portfolio):
            flash("Loyiha yangilandi!", "success")
            return redirect(url_for('admin_portfolio'))
        else:
            flash("Xatolik yuz berdi!", "error")
    
    # Convert tags list to comma-separated string for form
    if 'tags' in project and isinstance(project['tags'], list):
        project['tags_str'] = ', '.join(project['tags'])
    else:
        project['tags_str'] = ''
    
    return render_template('admin/portfolio_form.html', project=project)

@app.route('/admin/portfolio/delete/<int:project_id>')
@admin_required
def admin_portfolio_delete(project_id):
    portfolio = load_data(PORTFOLIO_FILE)
    portfolio = [p for p in portfolio if p.get('id') != project_id]
    
    if save_data(PORTFOLIO_FILE, portfolio):
        flash("Loyiha o'chirildi!", "success")
    else:
        flash("Xatolik yuz berdi!", "error")
    
    return redirect(url_for('admin_portfolio'))

# ========================
# BLOG MANAGEMENT
# ========================

@app.route('/admin/blog')
@admin_required
def admin_blog():
    blog_posts = load_data(BLOG_FILE)
    return render_template('admin/blog.html', blog_posts=blog_posts)

@app.route('/admin/blog/add', methods=['GET', 'POST'])
@admin_required
def admin_blog_add():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        excerpt = request.form.get('excerpt', '').strip()
        category = request.form.get('category', '').strip()
        image = request.form.get('image', '').strip()
        
        if not all([title, content, category]):
            flash("Majburiy maydonlarni to'ldiring!", "error")
        else:
            from datetime import datetime
            blog_posts = load_data(BLOG_FILE)
            new_id = max([b.get('id', 0) for b in blog_posts], default=0) + 1
            
            new_post = {
                'id': new_id,
                'title': title,
                'content': content,
                'excerpt': excerpt if excerpt else content[:200] + '...',
                'category': category,
                'date': datetime.now().strftime('%Y-%m-%d'),
                'image': image if image else 'default-blog.jpg'
            }
            
            blog_posts.append(new_post)
            if save_data(BLOG_FILE, blog_posts):
                flash("Yangi maqola qo'shildi!", "success")
                return redirect(url_for('admin_blog'))
            else:
                flash("Xatolik yuz berdi!", "error")
    
    return render_template('admin/blog_form.html')

@app.route('/admin/blog/edit/<int:post_id>', methods=['GET', 'POST'])
@admin_required
def admin_blog_edit(post_id):
    blog_posts = load_data(BLOG_FILE)
    post = next((b for b in blog_posts if b.get('id') == post_id), None)
    
    if not post:
        flash("Maqola topilmadi!", "error")
        return redirect(url_for('admin_blog'))
    
    if request.method == 'POST':
        post['title'] = request.form.get('title', '').strip()
        post['content'] = request.form.get('content', '').strip()
        post['excerpt'] = request.form.get('excerpt', '').strip()
        post['category'] = request.form.get('category', '').strip()
        post['image'] = request.form.get('image', '').strip() or 'default-blog.jpg'
        
        if save_data(BLOG_FILE, blog_posts):
            flash("Maqola yangilandi!", "success")
            return redirect(url_for('admin_blog'))
        else:
            flash("Xatolik yuz berdi!", "error")
    
    return render_template('admin/blog_form.html', post=post)

@app.route('/admin/blog/delete/<int:post_id>')
@admin_required
def admin_blog_delete(post_id):
    blog_posts = load_data(BLOG_FILE)
    blog_posts = [b for b in blog_posts if b.get('id') != post_id]
    
    if save_data(BLOG_FILE, blog_posts):
        flash("Maqola o'chirildi!", "success")
    else:
        flash("Xatolik yuz berdi!", "error")
    
    return redirect(url_for('admin_blog'))

# ========================
# MESSAGES MANAGEMENT
# ========================

@app.route('/admin/messages')
@admin_required
def admin_messages():
    messages = load_data(MESSAGES_FILE)
    # Sort by date, newest first
    messages.sort(key=lambda x: x.get('date', ''), reverse=True)
    return render_template('admin/messages.html', messages=messages)

@app.route('/admin/messages/mark_read/<int:message_id>')
@admin_required
def admin_message_mark_read(message_id):
    messages = load_data(MESSAGES_FILE)
    for message in messages:
        if message.get('id') == message_id:
            message['status'] = 'ko\'rilgan'
            break
    
    if save_data(MESSAGES_FILE, messages):
        flash("Xabar ko'rilgan deb belgilandi!", "success")
    else:
        flash("Xatolik yuz berdi!", "error")
    
    return redirect(url_for('admin_messages'))

@app.route('/admin/messages/delete/<int:message_id>')
@admin_required
def admin_message_delete(message_id):
    messages = load_data(MESSAGES_FILE)
    messages = [m for m in messages if m.get('id') != message_id]
    
    if save_data(MESSAGES_FILE, messages):
        flash("Xabar o'chirildi!", "success")
    else:
        flash("Xatolik yuz berdi!", "error")
    
    return redirect(url_for('admin_messages'))

@app.route('/admin/export/csv')
@admin_required
def export_messages_csv():
    """Export messages to CSV file"""
    import csv
    from io import StringIO
    from flask import Response
    
    messages = load_data(MESSAGES_FILE)
    
    def generate():
        output = StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow(['ID', 'Ism', 'Email', 'Telefon', 'Xizmat', 'Byudjet', 'Xabar', 'Sana', 'Holat', 'Telegram Yuborildi'])
        
        # Data
        for msg in messages:
            writer.writerow([
                msg.get('id', ''),
                msg.get('name', ''),
                msg.get('email', ''),
                msg.get('phone', ''),
                msg.get('service', ''),
                msg.get('budget', ''),
                msg.get('message', ''),
                msg.get('date', ''),
                msg.get('status', ''),
                'Ha' if msg.get('telegram_sent', False) else 'Yo\'q'
            ])
        
        output.seek(0)
        return output.read()
    
    from datetime import datetime
    filename = f"murojaatlar_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return Response(
        generate(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment;filename={filename}'}
    )

@app.route('/api/unread-count')
@admin_required
def api_unread_count():
    """API endpoint for real-time unread count"""
    messages = load_data(MESSAGES_FILE)
    unread_count = len([m for m in messages if m.get('status') == 'yangi'])
    return jsonify({'count': unread_count})

@app.route('/api/total-messages-count')
@admin_required
def api_total_messages_count():
    """API endpoint for total messages count"""
    messages = load_data(MESSAGES_FILE)
    return jsonify({'total': len(messages)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
