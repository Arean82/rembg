import os
import datetime
import configparser
import urllib.parse
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONFIG_FILE = os.path.join(ROOT_DIR, 'config.ini')

def get_config():
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)
    return config

class LocalImage(db.Model):
    __tablename__ = 'local_images'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(512), nullable=False)
    is_logged_in = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    expires_at = db.Column(db.DateTime)

    def __init__(self, **kwargs):
        super(LocalImage, self).__init__(**kwargs)

def init_db(app):
    config = get_config()
    
    # Portfolio PG Standard URI Construction
    user = config.get('POSTGRES', 'username', fallback='postgres')
    pw = urllib.parse.quote_plus(config.get('POSTGRES', 'password', fallback=''))
    host = config.get('POSTGRES', 'host', fallback='localhost')
    port = config.get('POSTGRES', 'port', fallback='5432')
    database = config.get('POSTGRES', 'database', fallback='synora_local')
    
    # Fallback logic: if it's explicitly set to sqlite in the DB name for dev
    if database.startswith('sqlite:///'):
        app.config['SQLALCHEMY_DATABASE_URI'] = database
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{user}:{pw}@{host}:{port}/{database}"
        
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    migrate.init_app(app, db)
    
    with app.app_context():
        db.create_all()

def log_image(filename, filepath, is_logged_in):
    config = get_config()
    
    if is_logged_in:
        retention_mins = config.getint('Retention', 'logged_in_retention_minutes', fallback=1440)
    else:
        retention_mins = config.getint('Retention', 'guest_retention_minutes', fallback=60)
        
    created_at = datetime.datetime.utcnow()
    expires_at = created_at + datetime.timedelta(minutes=retention_mins)
    
    new_image = LocalImage(
        filename=filename,
        filepath=filepath,
        is_logged_in=is_logged_in,
        created_at=created_at,
        expires_at=expires_at
    )
    db.session.add(new_image)
    db.session.commit()

def cleanup_expired_images(app=None):
    from sqlalchemy import func
    
    # Needs app context if running from background thread
    if app:
        with app.app_context():
            return _cleanup_logic()
    else:
        return _cleanup_logic()

def _cleanup_logic():
    now = datetime.datetime.utcnow()
    expired_images = LocalImage.query.filter(LocalImage.expires_at <= now).all()
    
    deleted_count = 0
    for img in expired_images:
        try:
            if os.path.exists(img.filepath):
                os.remove(img.filepath)
            db.session.delete(img)
            deleted_count += 1
            print(f"Deleted expired image: {img.filepath}")
        except Exception as e:
            print(f"Failed to delete {img.filepath}: {e}")
            
    if deleted_count > 0:
        db.session.commit()
        
    return deleted_count

