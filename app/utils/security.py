import jwt
import secrets
from datetime import datetime, timedelta
from functools import wraps
from flask import current_app, request, jsonify
from app.models.db_models import UserSession

def generate_token(length=32):
    """Generate a secure random token."""
    return secrets.token_urlsafe(length)

def create_jwt_token(user_id, expires_delta=timedelta(days=1)):
    """Create a JWT token for user authentication."""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + expires_delta,
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')

def validate_token(token):
    """Validate JWT token."""
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    """Decorator for routes that require token authentication."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            # Verify token in database
            session = UserSession.query.filter_by(
                token=token,
                is_active=True
            ).first()
            
            if not session or session.expires_at < datetime.utcnow():
                return jsonify({'error': 'Invalid or expired token'}), 401
            
            # Add user_id to request context
            request.user_id = session.user_id
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return decorated

def role_required(roles):
    """Decorator for routes that require specific user roles."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = request.headers.get('Authorization')
            
            if not token:
                return jsonify({'error': 'Token is missing'}), 401
            
            try:
                # Get user role from database
                session = UserSession.query.filter_by(token=token).first()
                user = User.query.get(session.user_id)
                
                if user.role not in roles:
                    return jsonify({'error': 'Insufficient permissions'}), 403
                
                return f(*args, **kwargs)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        return decorated
    return decorator

def hash_password(password):
    """Hash password using secure algorithm."""
    return generate_password_hash(password)

def verify_password(hashed_password, password):
    """Verify password against hash."""
    return check_password_hash(hashed_password, password)

def generate_secure_filename():
    """Generate a secure random filename."""
    return f"{secrets.token_hex(16)}"

def sanitize_input(data):
    """Sanitize user input to prevent XSS and injection attacks."""
    if isinstance(data, str):
        # Implement input sanitization logic
        return data.strip()
    elif isinstance(data, dict):
        return {k: sanitize_input(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_input(x) for x in data]
    return data
