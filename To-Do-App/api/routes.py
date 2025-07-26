from flask import Blueprint, request, jsonify,session,abort
from models import db, User, Task

api = Blueprint("api", __name__)


@api.route("/api/login", methods=["POST"])
def login_user():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid email or password"}), 401

    session['user_id'] = user.id
    session['user_name'] = user.full_name
    return jsonify({"message": "Login successful", "user": user.to_dict()}), 200


# === USERS ===
@api.route("/api/users", methods=["GET"])
def get_users():
    users = User.query.all()
    return jsonify([u.to_dict() for u in users]), 200


@api.route("/api/users/<int:id>", methods=["GET"])
def get_user(id):
    user = db.session.get(User, id)
    if user is None:
        abort(404)
    return jsonify(user.to_dict()), 200


# === TASKS ===
@api.route("/api/tasks", methods=["GET"])
def get_tasks():
    tasks = Task.query.all()
    return jsonify([t.to_dict() for t in tasks]), 200


@api.route("/api/tasks/<int:id>", methods=["GET"])
def get_task(id):
    task = db.session.get(Task, id)
    if task is None:
        abort(404)
    return jsonify(task.to_dict()), 200


@api.route("/api/tasks", methods=["POST"])
def create_task():
    data = request.get_json()
    title = data.get("title")
    user_id = session.get("user_id") or data.get("user_id")  # <-- added fallback for testing

    if not title or not user_id:
        return jsonify({"error": "Missing fields"}), 400

    task = Task(title=title, user_id=user_id)
    db.session.add(task)
    db.session.commit()
    return jsonify(task.to_dict()), 201


@api.route("/api/tasks/<int:id>", methods=["PUT"])
def update_task(id):
    task = db.session.get(Task, id)
    if task is None:
        abort(404)
    data = request.get_json()

    task.title = data.get("title", task.title)
    task.is_done = data.get("is_done", task.is_done)
    db.session.commit()

    return jsonify(task.to_dict()), 200


@api.route("/api/tasks/<int:id>", methods=["DELETE"])
def delete_task(id):
    task = db.session.get(Task, id)
    if task is None:
        abort(404)
    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Task deleted"}), 200


@api.route("/api/users", methods=["POST"])
def create_user():
    data = request.get_json()
    full_name = data.get("full_name")
    email = data.get("email")
    password = data.get("password")

    if not full_name or not email or not password:
        return jsonify({"error": "Missing fields"}), 400

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"error": "Email already exists"}), 409

    user = User(full_name=full_name, email=email)
    user.set_password(password) 
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201


