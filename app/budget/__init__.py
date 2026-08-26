from flask import Blueprint

bp = Blueprint('budget', __name__)

from app.budget import routes
