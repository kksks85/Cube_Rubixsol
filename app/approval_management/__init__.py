from flask import Blueprint

bp = Blueprint('approval_management', __name__, url_prefix='/approval-management')

from app.approval_management import routes
