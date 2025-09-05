# SmartBot.uz - Telegram Bot Development Platform

## Overview

SmartBot.uz is a professional Uzbek-language business website for a bot development and automation services company. The platform showcases services including Telegram bot development, chatbot creation, business automation solutions, and web development. Built as a Flask web application with integrated Google Gemini AI capabilities, it serves as a marketing and lead generation website for clients interested in bot development services in Uzbekistan.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Template Engine**: Jinja2 templating with Flask for server-side rendering
- **UI Framework**: Bootstrap 5 for responsive design and component library
- **Styling**: Custom CSS with CSS variables for theming and gradient backgrounds
- **Icons**: Font Awesome 6.4.0 for consistent iconography
- **Typography**: Google Fonts (Inter) for modern, readable text
- **JavaScript**: Vanilla JavaScript for interactive features like smooth scrolling, portfolio filtering, and form validation

### Backend Architecture
- **Web Framework**: Flask (Python) with simple route-based architecture
- **Application Structure**: Modular design with separate main.py entry point and app.py application logic
- **Session Management**: Flask sessions with configurable secret key from environment variables
- **Form Handling**: HTML forms with Flask request processing and flash messaging
- **Template Organization**: Hierarchical template structure with base.html extending to page-specific templates

### Routing Strategy
- **Static Pages**: Home, Services, Portfolio, About, Blog pages with GET-only routes
- **Contact Form**: POST/GET route with form validation and flash messaging
- **URL Structure**: Clean, SEO-friendly URLs in Uzbek language context

### Data Handling
- **Form Processing**: Basic validation for contact forms without database persistence
- **Flash Messaging**: User feedback system for form submissions and errors
- **Static Content**: Portfolio items, service descriptions, and blog content stored in templates

### Development Configuration
- **Debug Mode**: Enabled for development with detailed error logging
- **Logging**: Python logging configured at DEBUG level
- **Hot Reload**: Gunicorn with reload enabled for development
- **Host Configuration**: Configured for 0.0.0.0:5000 for Replit environment compatibility
- **Web Server**: Gunicorn WSGI server for both development and production

## External Dependencies

### Frontend Libraries
- **Bootstrap 5.3.0**: CSS framework from CDN for responsive components
- **Font Awesome 6.4.0**: Icon library from CDN for UI icons
- **Google Fonts**: Inter font family for typography

### Python Dependencies
- **Flask**: Core web framework for routing and templating
- **Werkzeug**: WSGI utilities (Flask dependency)
- **Jinja2**: Template engine (Flask dependency)
- **google-generativeai**: Google Gemini AI integration for intelligent features
- **PyPDF2**: PDF text extraction for document analysis
- **mimetypes**: File type detection for document uploads

### Infrastructure Requirements
- **Python 3.x**: Runtime environment
- **Web Server**: Flask development server (production would require WSGI server)
- **Static File Serving**: Flask static file handling for CSS/JS assets

### Environment Configuration
- **SESSION_SECRET**: Environment variable for Flask session security
- **PORT**: Configurable via Flask run parameters (default 5000)
- **DEBUG**: Controlled via Flask configuration
- **GEMINI_API_KEY**: Google Gemini API key for AI features

## AI Integration (September 2, 2025)

### Google Gemini 1.5 Flash Integration
SmartBot.uz now features comprehensive AI capabilities powered by Google Gemini 1.5 Flash model:

#### 5 Core AI Functions
1. **AI Chatbot** (`/ai/chat`): Intelligent assistant for website visitors with context-aware responses in Uzbek language
2. **Blog Auto-Generator** (`/ai/blog`): Creates SEO-optimized articles automatically from topic inputs
3. **Contact Form Analysis** (`/ai/analyze`): Analyzes messages and provides intelligent service recommendations
4. **Case Study Generator** (`/ai/case-study`): Creates detailed portfolio stories from project information
5. **Document Analysis** (`/ai/document`): Processes PDF files and extracts text for AI analysis

#### AI Interface
- **Dedicated AI Page**: `/ai` route with comprehensive interface for all AI tools
- **Interactive Frontend**: Real-time chat, file uploads, and dynamic results display
- **Professional UI**: Bootstrap-based design with loading states and error handling

#### Enhanced Features
- **Contact Form AI Enhancement**: Automatic service recommendations based on message analysis
- **Graceful Degradation**: Functions work without API key (provides user-friendly messages)
- **Uzbek Language Support**: All AI responses optimized for Uzbek language business context
- **SEO Integration**: AI-generated content includes proper meta tags and structured data

#### Technical Implementation
- **Backend**: Flask routes with comprehensive error handling and validation
- **Frontend**: Vanilla JavaScript with AJAX requests and dynamic UI updates  
- **Security**: File upload validation and temporary file cleanup
- **Performance**: Optimized prompts and response caching where appropriate

Note: The current implementation stores all content in JSON files and does not use a database. Contact form submissions are processed with AI analysis and include service recommendations. Blog articles generated by AI are automatically saved to the blog data file.