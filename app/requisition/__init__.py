from flask import Blueprint

bp = Blueprint('requisition', __name__)

from app.requisition import routes
