# ==================================================================
# File: web/web_main/i18n.py
# Description: 
# ==================================================================

from flask import request
from flask_babel import Babel

babel = Babel()

def get_locale():
    """
    Determine the best locale from cookies, otherwise default to English.
    """
    lang = request.cookies.get('lang')
    if lang in ['en', 'es', 'fr', 'de', 'zh', 'ja']:
        return lang
    
    # Fallback to browser's Accept-Language header
    return request.accept_languages.best_match(['en', 'es', 'fr', 'de', 'zh', 'ja']) or 'en'

def init_i18n(app):
    """
    Initialize Babel with the Flask app.
    """
    babel.init_app(app, locale_selector=get_locale)
