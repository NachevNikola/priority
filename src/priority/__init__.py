from flask import Flask

def create_app():
    app = Flask(__name__)

    app.config.from_object("src.config.settings")

    return app

app = create_app()

@app.get("/")
def index():
    return "Hello World!"
