import os
from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
import logging
import re

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "smartbot-uz-secret-key")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/portfolio')
def portfolio():
    return render_template('portfolio.html')

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
            # Simulate saving to database or sending email
            app.logger.info(f'New contact form submission from {name} ({email})')
            flash('Xabaringiz muvaffaqiyatli yuborildi! 24 soat ichida siz bilan bog\'lanamiz.', 'success')
            
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
