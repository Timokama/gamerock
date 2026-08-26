from flask import Blueprint

bp = Blueprint('treasurer', __name__)

from app.treasurer import routes
