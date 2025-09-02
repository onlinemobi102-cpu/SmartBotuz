# SmartBot.uz - Professional Telegram Bot Development Platform

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/Flask-3.1+-green.svg" alt="Flask">
  <img src="https://img.shields.io/badge/AI-Google%20Gemini-orange.svg" alt="AI">
  <img src="https://img.shields.io/badge/Deploy-Render-purple.svg" alt="Deploy">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
</div>

## 🚀 Loyiha Haqida

**SmartBot.uz** - bu O'zbekistondagi eng zamonaviy va to'liq funksional bot yaratish va avtomatlashtirish xizmatlari platformasi. Loyiha professional darajada ishlab chiqilgan va bizneslar uchun keng ko'lamli yechimlar taklif etadi.

### 🎯 Asosiy Maqsad
O'zbekiston bozorida bot development va avtomatlashtirish sohasini rivojlantirish, bizneslarni zamonaviy texnologiyalar bilan ta'minlash va AI texnologiyalarini mahalliy bozorga olib kirish.

## ✨ Asosiy Xususiyatlar

### 🤖 Bot Development Services
- **Telegram Bot Yaratish** - Professional telegram botlar
- **Chatbot Solutions** - Aqlli chat botlar
- **Business Automation** - Biznes jarayonlarini avtomatlashtirish
- **Web Development** - Zamonaviy veb-saytlar

### 🧠 AI Integration (Google Gemini 1.5 Flash)
1. **AI Chatbot** - Sayt tashrif buyuruvchilari uchun aqlli yordamchi
2. **Blog Auto-Generator** - Avtomatik maqola yaratish tizimi
3. **Contact Form Analysis** - Xabarlarni tahlil qilish va tavsiyalar
4. **Case Study Generator** - Portfolio hikoyalarini yaratish
5. **Document Analysis** - PDF hujjatlarni tahlil qilish

### 📱 Marketing Automation
- **AI Trend Analysis** - Avtomatik trend tahlili
- **Content Generation** - Kundalik 5 ta blog yaratish
- **Telegram Channel Integration** - Avtomatik post yuborish
- **SEO Optimization** - SEO optimallashtirilgan content

### 🎨 Modern Web Interface
- **Responsive Design** - Mobil va desktop uchun
- **Bootstrap 5** - Zamonaviy UI framework
- **Professional Design** - Biznes uchun professional ko'rinish
- **Multi-language Support** - O'zbek tili qo'llab-quvvatlash

## 🛠️ Texnologik Stack

### Backend
- **Flask 3.1+** - Python web framework
- **Gunicorn** - Production WSGI server
- **WhiteNoise** - Static file serving
- **Google Gemini AI** - AI integration
- **Telegram Bot API** - Bot functionality

### Frontend
- **Bootstrap 5.3** - CSS framework
- **Font Awesome 6.4** - Icons
- **Google Fonts** - Typography (Inter)
- **Vanilla JavaScript** - Interactive features

### Dependencies
```
flask>=3.1.2
google-generativeai>=0.8.5
python-telegram-bot>=21.0.1
gunicorn>=23.0.0
whitenoise>=6.9.0
pypdf2>=3.0.1
requests>=2.32.5
schedule>=1.2.2
```

## 📥 O'rnatish va Ishga Tushirish

### 1. Repository Clone Qilish
```bash
git clone https://github.com/your-username/smartbot-uz.git
cd smartbot-uz
```

### 2. Dependencies O'rnatish
```bash
pip install .
```

### 3. Environment Variables
`.env` fayl yarating:
```bash
FLASK_ENV=development
SESSION_SECRET=your-secret-key
ADMIN_PASSWORD=your-admin-password
GEMINI_API_KEY=your-gemini-api-key
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHAT_ID=your-chat-id
TELEGRAM_CHANNEL_ID=your-channel-id
```

### 4. Ishga Tushirish
```bash
python main.py
```

Sayt `http://localhost:5000` manzilida ochiladi.

## 🚀 Production Deploy (Render.com)

### 1. Environment Variables O'rnatish
Render dashboard da quyidagi o'zgaruvchilarni o'rnating:

**Majburiy:**
- `FLASK_ENV=production`
- `SESSION_SECRET` - Random secret key
- `ADMIN_PASSWORD` - Admin panel parol

**Ixtiyoriy (to'liq funksionallik uchun):**
- `GEMINI_API_KEY` - Google Gemini AI
- `TELEGRAM_BOT_TOKEN` - Telegram bot
- `TELEGRAM_CHAT_ID` - Xabarlar uchun
- `TELEGRAM_CHANNEL_ID` - Marketing uchun
- `GA_MEASUREMENT_ID` - Google Analytics
- `GOOGLE_VERIFICATION` - Search Console

### 2. Deploy
Repository ni Render.com ga ulang va `render.yaml` konfiguratsiyasidan foydalaning.

## 📊 Admin Panel

Admin panel `https://yoursite.com/admin` manzilida:

### Xususiyatlar:
- **Services Management** - Xizmatlarni boshqarish
- **Portfolio Management** - Portfolio loyihalarini qo'shish
- **Blog Management** - Blog maqolalarini yaratish
- **Messages View** - Mijozlar xabarlarini ko'rish
- **AI Marketing** - Marketing avtomatini boshqarish

### Kirish:
- Username: `admin`
- Password: `ADMIN_PASSWORD` environment variable

## 🤖 AI Marketing Avtomati

### Qanday Ishlaydi:
1. **Trend Analysis** - Gemini AI orqali zamonaviy trendlarni aniqlash
2. **Content Creation** - 5 ta SEO-optimized blog yaratish
3. **Auto Publishing** - Blog va Telegram kanaliga avtomatik yuborish
4. **Statistics** - Marketing natijalarini kuzatish

### Manual Ishga Tushirish:
Admin panelda "AI Marketing" bo'limidan qo'lda ishga tushirishingiz mumkin.

## 📞 API Endpoints

### Public Endpoints:
- `GET /` - Bosh sahifa
- `GET /services` - Xizmatlar
- `GET /portfolio` - Portfolio
- `GET /blog` - Blog
- `GET /about` - Biz haqimizda
- `GET /contact` - Bog'lanish
- `GET /ai` - AI Yordamchilar
- `POST /contact` - Contact form

### AI Endpoints:
- `POST /ai/chat` - AI chatbot
- `POST /ai/blog` - Blog generator
- `POST /ai/analyze` - Contact analysis
- `POST /ai/case-study` - Case study generator
- `POST /ai/document` - Document analysis

### Admin Endpoints:
- `GET /admin` - Admin dashboard
- `POST /admin/login` - Admin login
- `GET /admin/services` - Services management
- `GET /admin/portfolio` - Portfolio management
- `GET /admin/blog` - Blog management
- `GET /admin/messages` - Messages view
- `GET /admin/ai/marketing` - Marketing automation

## 🔧 Konfiguratsiya

### Data Files:
- `data/services.json` - Xizmatlar ma'lumotlari
- `data/portfolio.json` - Portfolio loyihalari
- `data/blog.json` - Blog maqolalari
- `data/messages.json` - Contact xabarlari

### Upload Folders:
- `static/uploads/` - File uploads
- `static/css/` - CSS files
- `static/js/` - JavaScript files

## 🎨 Customization

### CSS Variables:
```css
:root {
    --primary-color: #007bff;
    --secondary-color: #6c757d;
    --font-family: 'Inter', sans-serif;
}
```

### Template Structure:
```
templates/
├── base.html          # Base template
├── index.html         # Home page
├── services.html      # Services page
├── portfolio.html     # Portfolio page
├── blog.html          # Blog page
├── about.html         # About page
├── contact.html       # Contact page
├── ai.html           # AI interface
└── admin/            # Admin templates
```

## 📱 Mobile Optimization

- **Responsive Design** - Barcha ekran o'lchamlari uchun
- **Touch Friendly** - Mobil foydalanish uchun optimallashtirilgan
- **Fast Loading** - Tez yuklash
- **Mobile Navigation** - Mobil menyu

## 🔍 SEO Features

- **Meta Tags** - To'liq SEO meta tags
- **Structured Data** - Schema.org markup
- **Sitemap** - XML sitemap
- **Open Graph** - Social media sharing
- **Twitter Cards** - Twitter preview
- **Analytics** - Google Analytics integration

## 🔒 Security Features

- **Session Security** - Secure session cookies
- **Input Validation** - Form validation
- **File Upload Security** - Safe file handling
- **Environment Variables** - Sensitive data protection
- **Admin Authentication** - Password protection

## 📈 Performance

- **WhiteNoise** - Static file caching
- **Compression** - Gzip compression
- **CDN Integration** - External library CDN
- **Optimized Images** - Image optimization
- **Caching Headers** - Browser caching

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/YangiFunksiya`)
3. Commit changes (`git commit -am 'Yangi funksiya qo'shildi'`)
4. Push to branch (`git push origin feature/YangiFunksiya`)
5. Create Pull Request

## 📄 License

MIT License - `LICENSE` faylini ko'ring.

## 📞 Support

- **Website**: https://smartbot.uz
- **Email**: info@smartbot.uz
- **Telegram**: @smartbot_uz
- **Phone**: +998 90 123 45 67

## 🙏 Minnatdorchilik

- [Google Gemini](https://ai.google.dev/) - AI integration
- [Bootstrap](https://getbootstrap.com/) - CSS framework
- [Font Awesome](https://fontawesome.com/) - Icons
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [Render](https://render.com/) - Hosting platform

---

<div align="center">
  <p>Made with ❤️ in Uzbekistan</p>
  <p>© 2024 SmartBot.uz. Barcha huquqlar himoyalangan.</p>
</div>