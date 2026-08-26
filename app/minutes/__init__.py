from flask import Blueprint

bp = Blueprint('minutes', __name__)

from app.minutes import routes
