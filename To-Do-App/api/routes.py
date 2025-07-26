from flask import Blueprint, request, jsonify,session  
from models import db, User, Task

api = Blueprint("api", __name__)


@api.route("/api/login", methods=["POST"])
def login_user():
    """
    Login a user
    ---
    tags:
      - Users
    parameters:
      - in: body
        name: body
        required: true
        schema:
          properties:
            email:
              type: string
            password:
              type: string
    responses:
      200:
        description: Login success
      401:
        description: Invalid credentials
    """
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400

    user = User.query.filter_by(email=email, password=password).first()
    if not user:
        return jsonify({"error": "Invalid email or password"}), 401

    session['user_id'] = user.id
    return jsonify({"message": "Login successful", "user": user.to_dict()}), 200

# === USERS ===
@api.route("/api/users", methods=["GET"])
def get_users():
    users = User.query.all()
    return jsonify([u.to_dict() for u in users]), 200


@api.route("/api/users/<int:id>", methods=["GET"])
def get_user(id):
    """
    Get a specific user
    ---
    tags:
      - Users
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: A single user
    """
    user = User.query.get_or_404(id)
    return jsonify(user.to_dict()), 200


# === TASKS ===
@api.route("/api/tasks", methods=["GET"])
def get_tasks():
    """
    Get all tasks
    ---
    tags:
      - Tasks
    responses:
      200:
        description: A list of tasks
    """
    tasks = Task.query.all()
    return jsonify([t.to_dict() for t in tasks]), 200


@api.route("/api/tasks/<int:id>", methods=["GET"])
def get_task(id):
    """
    Get a specific task
    ---
    tags:
      - Tasks
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: A task
    """
    task = Task.query.get_or_404(id)
    return jsonify(task.to_dict()), 200


@api.route("/api/tasks", methods=["POST"])
def create_task():
    data = request.get_json()
    title = data.get("title")
    user_id = session.get("user_id")  # get user_id from session

    if not title or not user_id:
        return jsonify({"error": "Missing fields"}), 400

    task = Task(title=title, user_id=user_id)
    db.session.add(task)
    db.session.commit()
    return jsonify(task.to_dict()), 201



@api.route("/api/tasks/<int:id>", methods=["PUT"])
def update_task(id):
    """
    Update a task
    ---
    tags:
      - Tasks
    parameters:
      - name: id
        in: path
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          properties:
            title:
              type: string
            is_done:
              type: boolean
    responses:
      200:
        description: Task updated successfully
    """
    task = Task.query.get_or_404(id)
    data = request.get_json()

    task.title = data.get("title", task.title)
    task.is_done = data.get("is_done", task.is_done)
    db.session.commit()

    return jsonify(task.to_dict()), 200


@api.route("/api/tasks/<int:id>", methods=["DELETE"])
def delete_task(id):
    """
    Delete a task
    ---
    tags:
      - Tasks
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Task deleted successfully
    """
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Task deleted"}), 200



@api.route("/api/users", methods=["POST"])
def create_user():
    """
    Create a new user
    ---
    tags:
      - Users
    parameters:
      - in: body
        name: body
        required: true
        schema:
          properties:
            full_name:
              type: string
            email:
              type: string
            password:
              type: string
    responses:
      201:
        description: User created
      400:
        description: Missing fields
      409:
        description: Email already exists
    """
    data = request.get_json()
    full_name = data.get("full_name")
    email = data.get("email")
    password = data.get("password")

    if not full_name or not email or not password:
        return jsonify({"error": "Missing fields"}), 400

    # Check if email already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"error": "Email already exists"}), 409

    user = User(full_name=full_name, email=email, password=password)
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201

