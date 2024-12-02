from flask import Blueprint

bp = Blueprint('api', __name__)

from app.api import threat_detection, deep_fake, user_awareness
