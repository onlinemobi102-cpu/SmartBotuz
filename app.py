import os
from flask import Flask, render_template, request, flash, redirect, url_for, jsonify, session
from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix
from whitenoise import WhiteNoise
from functools import wraps
import logging
import re
import requests
import json
import uuid
import google.generativeai as genai
import mimetypes
import PyPDF2
from datetime import datetime
import base64
from io import BytesIO

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

# SEO Configuration
app.config['GA_MEASUREMENT_ID'] = os.environ.get("GA_MEASUREMENT_ID")
app.config['GOOGLE_VERIFICATION'] = os.environ.get("GOOGLE_VERIFICATION")

# Add WhiteNoise for static file serving with compression
app.wsgi_app = WhiteNoise(
    app.wsgi_app, 
    root='static/', 
    prefix='static/',
    max_age=31536000  # 1 year cache
)
app.wsgi_app.add_files('static/', prefix='static/')
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# Admin Configuration
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "smartbot123")

# AI Configuration
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    AI_MODEL = genai.GenerativeModel('gemini-1.5-flash')
else:
    AI_MODEL = None

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
        # Use the updated portfolio data from portfolio.json file
        pass
        
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

# ========================
# AI HELPER FUNCTIONS
# ========================

def get_ai_response(prompt, max_tokens=1000):
    """Get response from Gemini AI"""
    if not AI_MODEL:
        return None
    
    try:
        response = AI_MODEL.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=0.7,
            )
        )
        return response.text
    except Exception as e:
        app.logger.error(f"AI response error: {e}")
        return None

def analyze_text_with_ai(text, analysis_type="general"):
    """Analyze text with AI for different purposes"""
    if analysis_type == "contact":
        prompt = f"""
        Quyidagi mijoz murojatini tahlil qiling va eng mos xizmatni aniqlang:

        Murojaat matni: "{text}"

        Quyidagi xizmatlardan birini tanlang:
        - telegram_bot: Telegram bot yaratish
        - chatbot: AI chatbot integratsiya
        - automation: Biznes jarayonlarini avtomatlashtirish
        - web_development: Web sayt yaratish
        - ai_integration: AI texnologiyalar integratsiya

        Javobni faqat xizmat nomi bilan bering, boshqa hech narsa yozmang.
        """
    elif analysis_type == "document":
        prompt = f"""
        Quyidagi hujjat matnini tahlil qiling va mijoz ehtiyojlarini aniqlang:

        Hujjat matni: "{text}"

        Tahlil natijasini quyidagi formatda bering:
        - Asosiy maqsad: [maqsad]
        - Kerakli xizmatlar: [xizmatlar ro'yxati]
        - Tavsiya: [qisqa tavsiya]
        """
    else:
        prompt = f"Quyidagi matnni tahlil qiling: {text}"
    
    return get_ai_response(prompt, 500)

def create_blog_with_ai(topic):
    """Create SEO-optimized blog article with AI"""
    prompt = f"""
    "{topic}" mavzusida o'zbek tilida SEO optimallashtirilgan blog maqolasi yozing.

    Quyidagi strukturani kuzating:
    1. Jozibador sarlavha (50-60 belgi)
    2. Qisqa kirish (150-200 so'z)
    3. 3-4 ta asosiy bo'lim (har biri 200-300 so'z)
    4. Xulosa va chaqiruv (100-150 so'z)

    Shartlar:
    - Telegram bot, avtomatlashtirish, AI kabi kalit so'zlarni ishlating
    - Paragraflar qisqa va tushunarli bo'lsin
    - SmartBot.uz xizmatlariga ishoralar qiling
    - O'zbek tilida professional uslubda yozing

    Maqolani HTML formatida qaytaring, faqat <h2>, <p>, <ul>, <li> teglaridan foydalaning.
    """
    
    return get_ai_response(prompt, 2000)

def create_case_study_with_ai(project_info):
    """Create detailed case study with AI"""
    prompt = f"""
    Quyidagi loyiha ma'lumotlari asosida batafsil case study yarating:

    {project_info}

    Case study quyidagi bo'limlarni o'z ichiga olsin:
    1. Mijoz va muammo tavsifi
    2. Yechim strategiyasi
    3. Amalga oshirish jarayoni
    4. Foydalanilgan texnologiyalar
    5. Natijalar va ta'sir
    6. Mijoz fikri (qisqa)

    O'zbek tilida professional uslubda yozing, aniq raqamlar va faktlarni ko'rsating.
    """
    
    return get_ai_response(prompt, 1500)

def extract_text_from_pdf(file_path):
    """Extract text from PDF file"""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        app.logger.error(f"PDF extraction error: {e}")
        return None

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

# ========================
# MAIN ROUTES
# ========================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/portfolio')
def portfolio():
    portfolio_data = load_data(PORTFOLIO_FILE)
    return render_template('portfolio.html', portfolio=portfolio_data)

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
            
            # Save message to database
            message_saved = save_message(name, email, phone, service, budget, message)
            
            # AI Analysis of the message
            ai_recommendation = None
            if AI_MODEL:
                try:
                    analysis = analyze_text_with_ai(message, "contact")
                    service_map = {
                        'telegram_bot': 'Telegram Bot Yaratish',
                        'chatbot': 'AI Chatbot Integratsiya', 
                        'automation': 'Biznes Avtomatlashtirish',
                        'web_development': 'Web Sayt Yaratish',
                        'ai_integration': 'AI Texnologiyalar'
                    }
                    ai_recommendation = service_map.get(analysis.strip().lower(), 'Umumiy Konsultatsiya')
                except Exception as e:
                    app.logger.error(f"AI analysis error in contact form: {e}")
            
            # Update message with AI recommendation
            if message_saved and ai_recommendation:
                messages = load_data(MESSAGES_FILE)
                for msg in messages:
                    if msg['id'] == new_id:
                        msg['ai_recommendation'] = ai_recommendation
                        break
                save_data(MESSAGES_FILE, messages)
            
            # Send to Telegram
            telegram_sent = send_telegram_message(telegram_message)
            
            if message_saved:
                if telegram_sent:
                    flash("Xabaringiz muvaffaqiyatli yuborildi! Tez orada siz bilan bog'lanamiz.", "success")
                else:
                    flash("Xabaringiz saqlandi, lekin Telegram xabarnomasi yuborilmadi.", "warning")
            else:
                flash("Xatolik yuz berdi. Iltimos qaytadan urinib ko'ring.", "error")
                
            # Redirect to prevent form resubmission
            return redirect(url_for('contact'))
    
    return render_template('contact.html')

@app.route('/blog')
def blog():
    return render_template('blog.html')

# ========================
# SEO ROUTES
# ========================

@app.route('/sitemap.xml')
def sitemap():
    """Generate sitemap.xml for SEO"""
    with open('sitemap.xml', 'r', encoding='utf-8') as f:
        sitemap_content = f.read()
    response = app.response_class(sitemap_content, mimetype='application/xml')
    return response

@app.route('/robots.txt')
def robots_txt():
    """Generate robots.txt for SEO"""
    with open('robots.txt', 'r', encoding='utf-8') as f:
        robots_content = f.read()
    response = app.response_class(robots_content, mimetype='text/plain')
    return response

# ========================
# AI ROUTES
# ========================

@app.route('/ai/chat', methods=['POST'])
def ai_chat():
    """AI Chatbot for website visitors"""
    if not AI_MODEL:
        return jsonify({'error': 'AI xizmati mavjud emas'}), 503
    
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'error': 'Xabar bo\'sh bo\'lishi mumkin emas'}), 400
        
        # Create context-aware prompt for SmartBot.uz
        prompt = f"""
        Siz SmartBot.uz kompaniyasining AI yordamchisisiz. Mijoz bilan do'stona va professional tarzda gaplashing.

        Mijoz xabari: "{message}"

        Quyidagi qoidalarga rioya qiling:
        1. O'zbek tilida javob bering
        2. Qisqa va aniq javob bering (maksimal 200 so'z)
        3. Agar so'rov xizmatlar bilan bog'liq bo'lsa, tegishli sahifaga yo'naltiring
        4. SmartBot.uz xizmatlarini taklif qiling (Telegram botlar, chatbotlar, avtomatlashtirish)
        5. Do'stona va yordam beruvchi bo'ling

        SmartBot.uz xizmatlari:
        - Telegram bot yaratish (/services)
        - AI chatbot integratsiya (/services)
        - Biznes avtomatlashtirish (/services)
        - Web sayt yaratish (/services)
        - Portfolio: /portfolio
        - Bog'lanish: /contact
        """
        
        ai_response = get_ai_response(prompt, 300)
        
        if ai_response:
            return jsonify({
                'success': True,
                'response': ai_response
            })
        else:
            return jsonify({
                'success': False,
                'response': 'Kechirasiz, hozir javob bera olmayapman. Iltimos, keyinroq urinib ko\'ring.'
            })
            
    except Exception as e:
        app.logger.error(f"AI chat error: {e}")
        return jsonify({'error': 'Ichki xatolik yuz berdi'}), 500

@app.route('/ai/blog', methods=['POST'])
def ai_generate_blog():
    """Generate blog article with AI"""
    if not AI_MODEL:
        return jsonify({'error': 'AI xizmati mavjud emas'}), 503
    
    try:
        data = request.get_json()
        topic = data.get('topic', '').strip()
        
        if not topic:
            return jsonify({'error': 'Mavzu kiritilmagan'}), 400
        
        # Generate blog content
        blog_content = create_blog_with_ai(topic)
        
        if blog_content:
            # Save to blog data
            blogs = load_data(BLOG_FILE)
            new_id = max([b.get('id', 0) for b in blogs], default=0) + 1
            
            # Extract title from content (first h2 or first line)
            import re
            title_match = re.search(r'<h2>(.*?)</h2>', blog_content)
            title = title_match.group(1) if title_match else topic
            
            new_blog = {
                'id': new_id,
                'title': title,
                'content': blog_content,
                'excerpt': f"{topic} haqida batafsil ma'lumot",
                'category': 'AI Generated',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'slug': create_slug(title),
                'ai_generated': True
            }
            
            blogs.append(new_blog)
            save_data(BLOG_FILE, blogs)
            
            return jsonify({
                'success': True,
                'blog': new_blog,
                'message': 'Blog maqolasi muvaffaqiyatli yaratildi!'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Blog yaratishda xatolik yuz berdi'
            })
            
    except Exception as e:
        app.logger.error(f"AI blog generation error: {e}")
        return jsonify({'error': 'Ichki xatolik yuz berdi'}), 500

@app.route('/ai/analyze', methods=['POST'])
def ai_analyze_contact():
    """Analyze contact form submission"""
    if not AI_MODEL:
        return jsonify({'error': 'AI xizmati mavjud emas'}), 503
    
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'error': 'Tahlil qilish uchun matn kerak'}), 400
        
        # Analyze message
        analysis = analyze_text_with_ai(message, "contact")
        
        # Map analysis to service recommendations
        service_map = {
            'telegram_bot': {
                'service': 'Telegram Bot Yaratish',
                'description': 'Telegram bot orqali mijozlar bilan avtomatik aloqa',
                'url': '/services#telegram-bot'
            },
            'chatbot': {
                'service': 'AI Chatbot Integratsiya',
                'description': 'Saytingizga aqlli chatbot qo\'shish',
                'url': '/services#chatbot'
            },
            'automation': {
                'service': 'Biznes Avtomatlashtirish',
                'description': 'Biznes jarayonlarini avtomatlashtirish',
                'url': '/services#automation'
            },
            'web_development': {
                'service': 'Web Sayt Yaratish',
                'description': 'Professional web sayt yaratish',
                'url': '/services#web'
            },
            'ai_integration': {
                'service': 'AI Texnologiyalar',
                'description': 'AI va sun\'iy intellekt integratsiya',
                'url': '/services#ai'
            }
        }
        
        recommended_service = service_map.get(analysis.strip().lower(), {
            'service': 'Umumiy Konsultatsiya',
            'description': 'Ehtiyojlaringizni batafsil muhokama qilish',
            'url': '/contact'
        })
        
        return jsonify({
            'success': True,
            'analysis': analysis,
            'recommendation': recommended_service
        })
        
    except Exception as e:
        app.logger.error(f"AI analysis error: {e}")
        return jsonify({'error': 'Tahlil qilishda xatolik yuz berdi'}), 500

@app.route('/ai/case-study', methods=['POST'])
def ai_generate_case_study():
    """Generate portfolio case study with AI"""
    if not AI_MODEL:
        return jsonify({'error': 'AI xizmati mavjud emas'}), 503
    
    try:
        data = request.get_json()
        project_info = data.get('project_info', '').strip()
        
        if not project_info:
            return jsonify({'error': 'Loyiha ma\'lumotlari kiritilmagan'}), 400
        
        # Generate case study
        case_study = create_case_study_with_ai(project_info)
        
        if case_study:
            return jsonify({
                'success': True,
                'case_study': case_study,
                'message': 'Case study muvaffaqiyatli yaratildi!'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Case study yaratishda xatolik yuz berdi'
            })
            
    except Exception as e:
        app.logger.error(f"AI case study error: {e}")
        return jsonify({'error': 'Ichki xatolik yuz berdi'}), 500

@app.route('/ai/document', methods=['POST'])
def ai_analyze_document():
    """Analyze uploaded document (PDF/image)"""
    if not AI_MODEL:
        return jsonify({'error': 'AI xizmati mavjud emas'}), 503
    
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Fayl yuklanmagan'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Fayl tanlanmagan'}), 400
        
        # Check file type
        file_type = mimetypes.guess_type(file.filename)[0]
        
        if file_type and file_type.startswith('application/pdf'):
            # Save temporarily and extract text
            temp_path = os.path.join(app.config['UPLOAD_FOLDER'], f"temp_{uuid.uuid4().hex}.pdf")
            file.save(temp_path)
            
            try:
                extracted_text = extract_text_from_pdf(temp_path)
                os.remove(temp_path)  # Clean up
                
                if extracted_text:
                    analysis = analyze_text_with_ai(extracted_text, "document")
                    
                    return jsonify({
                        'success': True,
                        'file_type': 'PDF',
                        'extracted_text': extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text,
                        'analysis': analysis
                    })
                else:
                    return jsonify({
                        'success': False,
                        'message': 'PDF dan matn ajratib olinmadi'
                    })
                    
            except Exception as e:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                raise e
                
        elif file_type and file_type.startswith('image/'):
            # For images, we can only provide basic info
            return jsonify({
                'success': True,
                'file_type': 'Image',
                'message': 'Rasm fayli yuklandi. Matn tahlili uchun PDF fayl yuklang.',
                'analysis': 'Rasm fayllari uchun matn tahlili hozircha mavjud emas. PDF formatida hujjat yuklashni tavsiya qilamiz.'
            })
        else:
            return jsonify({'error': 'Faqat PDF va rasm fayllari qo\'llab-quvvatlanadi'}), 400
            
    except Exception as e:
        app.logger.error(f"AI document analysis error: {e}")
        return jsonify({'error': 'Hujjat tahlilida xatolik yuz berdi'}), 500

# AI Interface Page
@app.route('/ai')
def ai_interface():
    """AI tools interface page"""
    return render_template('ai.html')

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
    
    # Count AI generated posts today
    ai_posts_count = get_today_posts_count()
    
    stats = {
        'services': services_count,
        'portfolio': portfolio_count,
        'blog': blog_count,
        'messages': messages_count,
        'new_messages': new_messages_count,
        'ai_posts': ai_posts_count
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
# BLOG MANAGEMENT
# ========================

@app.route('/admin/blog')
@admin_required
def admin_blog():
    blogs = load_data(BLOG_FILE)
    return render_template('admin/blog.html', blogs=blogs)

@app.route('/admin/blog/add', methods=['GET', 'POST'])
@admin_required
def admin_blog_add():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        excerpt = request.form.get('excerpt', '').strip()
        category = request.form.get('category', '').strip()
        
        if not all([title, content, excerpt, category]):
            flash("Barcha maydonlarni to'ldiring!", "error")
        else:
            blogs = load_data(BLOG_FILE)
            new_id = max([b.get('id', 0) for b in blogs], default=0) + 1
            
            new_blog = {
                'id': new_id,
                'title': title,
                'content': content,
                'excerpt': excerpt,
                'category': category,
                'date': datetime.now().strftime('%Y-%m-%d'),
                'slug': create_slug(title)
            }
            
            blogs.append(new_blog)
            if save_data(BLOG_FILE, blogs):
                flash("Yangi maqola qo'shildi!", "success")
                return redirect(url_for('admin_blog'))
            else:
                flash("Xatolik yuz berdi!", "error")
    
    return render_template('admin/blog_form.html')

@app.route('/admin/blog/edit/<int:blog_id>', methods=['GET', 'POST'])
@admin_required
def admin_blog_edit(blog_id):
    blogs = load_data(BLOG_FILE)
    blog = next((b for b in blogs if b.get('id') == blog_id), None)
    
    if not blog:
        flash("Maqola topilmadi!", "error")
        return redirect(url_for('admin_blog'))
    
    if request.method == 'POST':
        blog['title'] = request.form.get('title', '').strip()
        blog['content'] = request.form.get('content', '').strip()
        blog['excerpt'] = request.form.get('excerpt', '').strip()
        blog['category'] = request.form.get('category', '').strip()
        blog['slug'] = create_slug(blog['title'])
        
        if save_data(BLOG_FILE, blogs):
            flash("Maqola yangilandi!", "success")
            return redirect(url_for('admin_blog'))
        else:
            flash("Xatolik yuz berdi!", "error")
    
    return render_template('admin/blog_form.html', blog=blog)

@app.route('/admin/blog/delete/<int:blog_id>')
@admin_required
def admin_blog_delete(blog_id):
    blogs = load_data(BLOG_FILE)
    blogs = [b for b in blogs if b.get('id') != blog_id]
    
    if save_data(BLOG_FILE, blogs):
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
    # Reverse order - yangi messages birinchi
    messages = sorted(messages, key=lambda x: x.get('date', ''), reverse=True)
    return render_template('admin/messages.html', messages=messages)

@app.route('/admin/messages/mark-read/<int:message_id>')
@admin_required
def admin_message_mark_read(message_id):
    messages = load_data(MESSAGES_FILE)
    for message in messages:
        if message.get('id') == message_id:
            message['status'] = 'ko\'rilgan'
            break
    
    if save_data(MESSAGES_FILE, messages):
        flash("Xabar o'qilgan deb belgilandi!", "success")
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

@app.route('/admin/messages/export-csv')
@admin_required
def export_messages_csv():
    """Export messages to CSV"""
    import csv
    from io import StringIO
    from flask import make_response
    
    messages = load_data(MESSAGES_FILE)
    
    output = StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(['ID', 'Ism', 'Email', 'Telefon', 'Xizmat', 'Byudjet', 'Xabar', 'Sana', 'Status'])
    
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
            msg.get('status', '')
        ])
    
    output.seek(0)
    
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=messages_{datetime.now().strftime("%Y%m%d")}.csv'
    
    return response

@app.route('/api/unread-count')
def api_unread_count():
    """API endpoint for unread messages count"""
    messages = load_data(MESSAGES_FILE)
    unread_count = len([m for m in messages if m.get('status') == 'yangi'])
    return jsonify({'count': unread_count})

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
        category = request.form.get('category', '').strip()
        tags = request.form.get('tags', '').strip()
        
        # Additional fields for detail page
        client = request.form.get('client', '').strip()
        duration = request.form.get('duration', '').strip()
        price = request.form.get('price', '').strip()
        problem = request.form.get('problem', '').strip()
        solution = request.form.get('solution', '').strip()
        features_text = request.form.get('features', '').strip()
        results_text = request.form.get('results', '').strip()
        technologies_text = request.form.get('technologies', '').strip()
        
        if not all([title, description, category]):
            flash("Majburiy maydonlarni to'ldiring!", "error")
        else:
            portfolio = load_data(PORTFOLIO_FILE)
            new_id = max([p.get('id', 0) for p in portfolio], default=0) + 1
            
            # Generate slug
            slug = create_slug(title)
            
            # Process tags, features, results, technologies
            tags_list = [tag.strip() for tag in tags.split(',') if tag.strip()] if tags else []
            features_list = [f.strip() for f in features_text.split('\n') if f.strip()] if features_text else []
            results_list = [r.strip() for r in results_text.split('\n') if r.strip()] if results_text else []
            technologies_list = [t.strip() for t in technologies_text.split(',') if t.strip()] if technologies_text else []
            
            # Handle file upload
            image_filename = 'default-portfolio.jpg'
            if 'image' in request.files:
                file = request.files['image']
                if file.filename and file.filename != '' and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    unique_filename = f"{new_id}_{filename}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
                    image_filename = unique_filename
            
            new_project = {
                'id': new_id,
                'title': title,
                'slug': slug,
                'description': description,
                'short_description': description,
                'image': image_filename,
                'tags': tags_list,
                'category': category,
                'client': client if client else 'Mijoz',
                'duration': duration if duration else 'N/A',
                'price': price if price else 'Kelishilgan narxda',
                'status': 'Muvaffaqiyatli yakunlandi',
                'gradient': 'primary',
                'icon': 'fas fa-laptop-code',
                'problem': problem if problem else description,
                'solution': solution if solution else description,
                'features': features_list,
                'results': results_list,
                'technologies': technologies_list
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
        project['category'] = request.form.get('category', '').strip()
        
        # Additional fields
        project['client'] = request.form.get('client', '').strip()
        project['duration'] = request.form.get('duration', '').strip()
        project['price'] = request.form.get('price', '').strip()
        project['problem'] = request.form.get('problem', '').strip()
        project['solution'] = request.form.get('solution', '').strip()
        
        # Process tags, features, results, technologies
        tags = request.form.get('tags', '').strip()
        project['tags'] = [tag.strip() for tag in tags.split(',') if tag.strip()] if tags else []
        
        features_text = request.form.get('features', '').strip()
        project['features'] = [f.strip() for f in features_text.split('\n') if f.strip()] if features_text else []
        
        results_text = request.form.get('results', '').strip()
        project['results'] = [r.strip() for r in results_text.split('\n') if r.strip()] if results_text else []
        
        technologies_text = request.form.get('technologies', '').strip()
        project['technologies'] = [t.strip() for t in technologies_text.split(',') if t.strip()] if technologies_text else []
        
        # Update slug if title changed
        project['slug'] = create_slug(project['title'])
        
        # Handle file upload
        if 'image' in request.files:
            file = request.files['image']
            if file.filename and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_filename = f"{project_id}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
                project['image'] = unique_filename
        
        if save_data(PORTFOLIO_FILE, portfolio):
            flash("Loyiha yangilandi!", "success")
            return redirect(url_for('admin_portfolio'))
        else:
            flash("Xatolik yuz berdi!", "error")
    
    # Convert lists to strings for form display
    if 'tags' in project and isinstance(project['tags'], list):
        project['tags_str'] = ', '.join(project['tags'])
    else:
        project['tags_str'] = ''
        
    if 'features' in project and isinstance(project['features'], list):
        project['features_str'] = '\n'.join(project['features'])
    else:
        project['features_str'] = ''
        
    if 'results' in project and isinstance(project['results'], list):
        project['results_str'] = '\n'.join(project['results'])
    else:
        project['results_str'] = ''
        
    if 'technologies' in project and isinstance(project['technologies'], list):
        project['technologies_str'] = ', '.join(project['technologies'])
    else:
        project['technologies_str'] = ''
    
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
# AI MARKETING AUTOMATION
# ========================

@app.route('/admin/ai/marketing')
@admin_required
def admin_ai_marketing():
    """AI Marketing Avtomat sahifasi"""
    # Get last run data
    last_run = get_last_marketing_run()
    today_posts = get_today_posts_count()
    
    return render_template('admin/ai_marketing.html', 
                          last_run=last_run, 
                          today_posts=today_posts)

@app.route('/admin/ai/marketing/run', methods=['POST'])
@admin_required
def ai_daily_marketing():
    """Kundalik AI marketing jarayoni"""
    if not AI_MODEL:
        return jsonify({'success': False, 'error': 'AI xizmati mavjud emas'}), 503
    
    try:
        # 1. Trendlarni olish
        trends = get_latest_trends()
        
        # 2. Blog postlari yaratish
        posts = []
        for i, trend in enumerate(trends[:5]):
            try:
                # AI orqali blog post yaratish
                post_content = create_trending_blog_post(trend)
                
                if post_content:
                    # Sarlavhani chiqarish
                    title = extract_title_from_content(post_content)
                    
                    # Blog ma'lumotlarini saqlash
                    blogs = load_data(BLOG_FILE)
                    new_id = max([b.get('id', 0) for b in blogs], default=0) + 1
                    
                    new_post = {
                        'id': new_id,
                        'title': title,
                        'content': post_content,
                        'excerpt': f"{trend} haqida batafsil ma'lumot va tahlil",
                        'category': 'AI Trend',
                        'date': datetime.now().strftime('%Y-%m-%d'),
                        'slug': create_slug(title),
                        'ai_generated': True,
                        'trend_topic': trend
                    }
                    
                    blogs.append(new_post)
                    save_data(BLOG_FILE, blogs)
                    posts.append(new_post)
                    
                    # Telegram kanaliga yuborish
                    send_to_telegram_channel(new_post)
                    
                    app.logger.info(f"AI blog post created: {title}")
                    
            except Exception as e:
                app.logger.error(f"Error creating blog post for trend '{trend}': {e}")
                continue
        
        # 3. Marketing run ma'lumotlarini saqlash
        save_marketing_run_data(len(posts))
        
        return jsonify({
            'success': True,
            'posts': posts,
            'count': len(posts),
            'message': f'{len(posts)} ta yangi blog posti yaratildi va Telegram kanaliga yuborildi!'
        })
        
    except Exception as e:
        app.logger.error(f"AI marketing error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

def get_latest_trends():
    """So'nggi trendlarni olish"""
    # Asosiy IT/AI trendlar ro'yxati
    base_trends = [
        "Telegram bot biznes uchun afzalliklari",
        "AI chatbot sayt uchun",
        "2025 yilda avtomatlashtirish tendensiyalari", 
        "SmartBot texnologiyalari yangiliklari",
        "O'zbekistonda digital transformatsiya",
        "Telegram mini-app rivojlanishi",
        "AI marketing vositalari",
        "Biznes jarayonlarini optimallashtirish",
        "Chatbot integratsiya usullari",
        "Digital biznes yechimlar"
    ]
    
    # Tasodifiy 5 ta trendni qaytarish
    import random
    return random.sample(base_trends, 5)

def create_trending_blog_post(trend_topic):
    """Trend mavzusi bo'yicha blog post yaratish"""
    prompt = f"""
    O'zbek tilida professional SEO optimallashtirilgan blog maqolasi yozing:
    
    Mavzu: {trend_topic}
    
    Talablar:
    1. Sarlavha: Jozibador va SEO uchun optimallashtirilgan (50-70 belgi)
    2. Kirish: 2-3 paragraf, muammoni aniqlash
    3. Asosiy qism: 4-5 ta bo'lim, har biri 150-250 so'z
    4. Misollar: Real hayot misollari va statistikalar
    5. Xulosa: Amaliy tavsiyalar va chaqiruv
    6. Kalit so'zlar: {trend_topic}, SmartBot.uz, avtomatlashtirish, AI
    
    Uslub:
    - Professional lekin tushunarli
    - O'zbek biznes auditoriyasi uchun
    - SmartBot.uz xizmatlariga tabiiy ishoralar
    - Paragraflar orasida bo'sh qator
    
    HTML formatda yozing, faqat <h2>, <h3>, <p>, <strong>, <ul>, <li> teglaridan foydalaning.
    """
    
    return get_ai_response(prompt, 2500)

def extract_title_from_content(content):
    """Kontent ichidan sarlavhani chiqarish"""
    try:
        import re
        # HTML h2 tagidan sarlavhani topish
        title_match = re.search(r'<h2>(.*?)</h2>', content, re.IGNORECASE)
        if title_match:
            return title_match.group(1).strip()
        
        # Agar h2 yo'q bo'lsa, birinchi paragrafdan olish
        para_match = re.search(r'<p><strong>(.*?)</strong></p>', content, re.IGNORECASE)
        if para_match:
            return para_match.group(1).strip()
            
        # Agar boshqa formatda bo'lsa
        lines = content.split('\n')
        for line in lines[:5]:  # Birinchi 5 qatordan qidirish
            clean_line = re.sub(r'<[^>]+>', '', line).strip()
            if clean_line and len(clean_line) > 10:
                return clean_line[:100]  # Maksimal 100 belgi
                
        return "AI Blog Posti"
    except:
        return "AI Blog Posti"

def send_to_telegram_channel(post):
    """Blog postini Telegram kanaliga yuborish"""
    if not TELEGRAM_BOT_TOKEN:
        return False
        
    try:
        # Kanal username yoki chat_id ni aniqlash
        channel_username = "@smartbotuz"  # O'zgartiring
        
        # Postni qisqartirish
        excerpt = post.get('excerpt', '')
        if not excerpt:
            # Content dan qisqa matn yaratish
            import re
            clean_content = re.sub(r'<[^>]+>', '', post['content'])
            excerpt = clean_content[:200] + '...' if len(clean_content) > 200 else clean_content
        
        # Telegram xabari
        message = f"""📢 YANGI MAQOLA

🎯 {post['title']}

{excerpt}

📖 To'liq maqolani o'qing: https://smartbot.uz/blog/{post['slug']}

#SmartBotUz #AI #Trend #Blog"""
        
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            'chat_id': channel_username,
            'text': message,
            'parse_mode': 'HTML',
            'disable_web_page_preview': False
        }
        
        response = requests.post(url, data=data, timeout=10)
        return response.status_code == 200
        
    except Exception as e:
        app.logger.error(f"Telegram yuborishda xatolik: {e}")
        return False

def get_last_marketing_run():
    """So'nggi marketing run ma'lumotini olish"""
    try:
        marketing_file = os.path.join(DATA_DIR, "marketing_runs.json")
        if os.path.exists(marketing_file):
            data = load_data(marketing_file)
            if data:
                last_run = max(data, key=lambda x: x.get('date', ''))
                return last_run.get('date', 'Hech qachon')
        return 'Hech qachon'
    except:
        return 'Hech qachon'

def get_today_posts_count():
    """Bugungi postlar sonini olish"""
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        blogs = load_data(BLOG_FILE)
        today_posts = [b for b in blogs if b.get('date') == today and b.get('ai_generated')]
        return len(today_posts)
    except:
        return 0

def save_marketing_run_data(posts_count):
    """Marketing run ma'lumotlarini saqlash"""
    try:
        marketing_file = os.path.join(DATA_DIR, "marketing_runs.json")
        runs = load_data(marketing_file) if os.path.exists(marketing_file) else []
        
        new_run = {
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'posts_count': posts_count,
            'status': 'success'
        }
        
        runs.append(new_run)
        save_data(marketing_file, runs)
        
    except Exception as e:
        app.logger.error(f"Marketing run ma'lumotlarini saqlashda xatolik: {e}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)