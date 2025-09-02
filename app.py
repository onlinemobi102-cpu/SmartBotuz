import os
from flask import Flask, render_template, request, flash, redirect, url_for
import logging

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
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        
        # Basic validation
        if not all([name, email, message]):
            flash('Iltimos, barcha majburiy maydonlarni to\'ldiring.', 'error')
        else:
            # In a real application, you would save this to a database or send an email
            flash('Xabaringiz muvaffaqiyatli yuborildi! Tez orada siz bilan bog\'lanamiz.', 'success')
            return redirect(url_for('contact'))
    
    return render_template('contact.html')

@app.route('/blog')
def blog():
    return render_template('blog.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
