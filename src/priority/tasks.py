from flask import Blueprint

tasks = Blueprint("tasks", __name__, url_prefix="/api/tasks")

@tasks.get("/")
def get_tasks():
    return {"result": []}

@tasks.post("/")
def create_task():
    return {"result": "ok"}
