from flask import Blueprint

bp = Blueprint('uav_service', __name__)

from app.uav_service import routes
