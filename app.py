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
                if file.filename != '' and allowed_file(file.filename):
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
            if file.filename != '' and allowed_file(file.filename):
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)