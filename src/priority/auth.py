from flask import Blueprint

auth = Blueprint("auth", __name__, url_prefix="/api/auth")

@auth.post("/register")
def register():
    return {"result": "ok"}

@auth.post("/login")
def login():
    return {"result": "jwt"}
