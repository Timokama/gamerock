from flask import Blueprint

bp = Blueprint('sponsor', __name__)

from app.sponsor import routes
