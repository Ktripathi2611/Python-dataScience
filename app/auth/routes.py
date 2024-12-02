from flask import jsonify, request
from app.auth import bp
from app.models.db_models import User, UserSession
from app.utils.security import generate_token, validate_token
from datetime import datetime, timedelta

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Validate required fields
    if not all(k in data for k in ('username', 'email', 'password')):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if user already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    # Create new user
    user = User(username=data['username'], email=data['email'])
    user.set_password(data['password'])
    
    try:
        db.session.add(user)
        db.session.commit()
        return jsonify({
            'message': 'User registered successfully',
            'user_id': user.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    # Validate required fields
    if not all(k in data for k in ('username', 'password')):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Find user
    user = User.query.filter_by(username=data['username']).first()
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid username or password'}), 401
    
    try:
        # Generate session token
        token = generate_token()
        expires_at = datetime.utcnow() + timedelta(days=1)
        
        # Create session
        session = UserSession(
            user_id=user.id,
            token=token,
            device_info=request.headers.get('User-Agent'),
            expires_at=expires_at
        )
        
        db.session.add(session)
        db.session.commit()
        
        return jsonify({
            'token': token,
            'expires_at': expires_at.isoformat(),
            'user': {
                'id': user.id,
                'username': user.username,
                'role': user.role
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/logout', methods=['POST'])
def logout():
    auth_token = request.headers.get('Authorization')
    if not auth_token:
        return jsonify({'error': 'No token provided'}), 401
    
    try:
        # Invalidate session
        session = UserSession.query.filter_by(token=auth_token).first()
        if session:
            session.is_active = False
            db.session.commit()
        
        return jsonify({'message': 'Logged out successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    
    # Validate email
    if 'email' not in data:
        return jsonify({'error': 'Email is required'}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    if not user:
        return jsonify({'error': 'Email not found'}), 404
    
    try:
        # Generate reset token and send email
        reset_token = generate_token()
        # TODO: Implement email sending logic
        
        return jsonify({'message': 'Password reset instructions sent'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/verify-token', methods=['POST'])
def verify_token():
    auth_token = request.headers.get('Authorization')
    if not auth_token:
        return jsonify({'error': 'No token provided'}), 401
    
    try:
        # Verify token and session
        session = UserSession.query.filter_by(
            token=auth_token,
            is_active=True
        ).first()
        
        if not session or session.expires_at < datetime.utcnow():
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        return jsonify({'valid': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
