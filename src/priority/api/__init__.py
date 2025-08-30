from flask import Blueprint

api = Blueprint("api", __name__, url_prefix="/api")

from .me import *
from .rules import *
from .tasks import *
